from email.policy import default

from docutils.nodes import comment
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class PaymentVoucher(models.Model):
    _name = 'payment.voucher'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Payment Voucher'

    name = fields.Char(string="Voucher Number", required=True, copy=False, readonly=True, default="/")

    projects = fields.Selection([
        ('special', 'Special Project'),
        ('state', 'State'),
        ('expenditure', 'Expenditure'),
    ], string="Unit", tracking=True)
    date = fields.Date(string="Date", required=True, default=fields.Date.context_today)
    voucher_ref = fields.Char(string="Voucher Ref", copy=False, tracking=True)
    file_no = fields.Char(string="File No", tracking=True, copy=False)
    transaction_date = fields.Date(string="Transaction Date", tracking=True, required=True)
    payee_id = fields.Many2one('res.partner', string="Payee", copy=False, tracking=True, required=True)
    contract_value = fields.Monetary(string="Contract Value", currency_field='currency_id', copy=False, tracking=True,
                                     required=True)
    outstanding_debits = fields.Monetary(string="Outstanding Debits", currency_field='currency_id',
                                         compute="_compute_outstanding_debits", copy=False)

    expense_account_id = fields.Many2one('account.account', string="Expense Account",
                                         domain=[('account_type', '=', 'expense')], copy=False, tracking=True,
                                         required=True)

    purpose = fields.Text(string="Purpose of Expenditure", copy=False, tracking=True, required=True)
    attachment_ids = fields.Many2many('ir.attachment', copy=False, string="Supporting Documents")
    # Approval Workflow
    state = fields.Selection([
        ('draft', 'Draft'),
        ('prepared', 'Prepared'),
        ('cancel', 'Cancelled'),
    ], string="Status", default="draft", tracking=True)
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='company_id.currency_id',
        readonly=True
    )
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    prepared_by = fields.Many2one('res.users', string="Prepared By", tracking=True)
    checked_by = fields.Many2one('res.users', string="Checked By", tracking=True)
    cancelled_by = fields.Many2one('res.users', string="Authorized By", tracking=True)

    comments = fields.Text(string="Comments")
    voucher_count = fields.Integer(string="Payment Vouchers", compute="compute_voucher_count", copy=False)

    journal_id = fields.Many2one('account.journal', )
    journal_count = fields.Integer(compute="compute_journal_count", string="Journal Items", copy=False)

    # Approval Log
    approval_log_ids = fields.One2many('approval.log.line', 'voucher_id', string="Approval Log")
    partial_paid = fields.Boolean(copy=False, default=False, compute="_update_payment_status", store=True)
    fully_paid = fields.Boolean(copy=False, default=False, compute="_update_payment_status", store=True)

    is_locked = fields.Boolean(string='Locked', copy=False)

    @api.onchange('purpose')
    def _onchange_purpose(self):
        if self.purpose:
            self.purpose = self.purpose.upper()

    def action_lock(self):
        for rec in self:
            rec.is_locked = True

    def action_unlock(self):
        for rec in self:
            rec.is_locked = False

    @api.onchange('outstanding_debits')
    def _update_payment_status(self):
        for voucher in self:
            if voucher.state == 'prepared':
                _logger.info(f"Updating payment status for voucher ID: {voucher.id} in 'prepared' state")

                # Search for related payments using the voucher name in the 'ref' field
                payments = self.env['payment.voucher.breakdown'].search([
                    ('voucher_id', '=', voucher.id),
                    ('state', '=', 'done')
                ])
                _logger.info(f"Found {len(payments)} payment(s) in 'done' state for voucher ID: {voucher.id}")

                total = payments.mapped('amount_to_paid') or 0.0
                total_paid = float(sum(payments.mapped('amount_to_paid')))
                contract_value = float(voucher.contract_value or 0.0)

                # Optional: Round both to avoid floating point precision issues
                total_paid = round(total_paid, 2)
                contract_value = round(contract_value, 2)
                _logger.info(f"Total Paid: {total_paid}, Contract Value: {contract_value}")

                # Reset flags
                voucher.partial_paid = False
                voucher.fully_paid = False
                if total_paid == contract_value:
                    voucher.fully_paid = True
                    _logger.info(f"Voucher ID: {voucher.id} marked as fully paid.")
                elif total_paid != 0.0:
                    voucher.partial_paid = True
                    _logger.info(f"Voucher ID: {voucher.id} marked as partially paid.")
                else:
                    _logger.info(f"No payments made for voucher ID: {voucher.id}.")

    def view_journal_entries(self):
        jv_ids = self.env['account.move'].search_count([('ref', '=', self.name)])
        return {
            'name': 'Journal Entries',
            'view_type': 'form',
            'view_mode': 'list,form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'views': [(False, 'list'), (False, 'form')],
            'domain': [('ref', '=', self.name)],
        }

    def create_journal_entries(self):
        for voucher in self:
            if not voucher.payee_id.property_account_payable_id:
                raise UserError("Payee has no payable account configured.")
            if not voucher.expense_account_id:
                raise UserError("Please select an expense account.")

            if self.payee_id.customer_rank > 0:
                journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
            elif self.payee_id.supplier_rank > 0:
                journal = self.env['account.journal'].search([('type', '=', 'purchase')], limit=1)
            elif self.payee_id.employee_ids:
                journal = self.env['account.journal'].search([('type', '=', 'general')], limit=1)
            else:
                raise UserError("Cannot determine journal: payee must be either a customer or a vendor.")

            if not journal:
                raise UserError("No appropriate journal found for the payee type.")

            move_vals = {
                'ref': voucher.name,
                'date': voucher.transaction_date or fields.Date.today(),
                'journal_id': journal.id,
                'partner_id': voucher.payee_id.id,
                'line_ids': [],
                # 'origin': f"Payment Voucher: {voucher.name}",
            }

            # Debit line: Expense Account
            debit_line = (0, 0, {
                'account_id': voucher.expense_account_id.id,
                'partner_id': voucher.payee_id.id,
                'name': voucher.purpose or '/',
                'debit': voucher.contract_value,
                'credit': 0.0,
            })

            # Credit line: Journal's Default Credit Account
            credit_account_id = voucher.payee_id.property_account_payable_id.id
            if not credit_account_id:
                raise UserError("Selected journal has no default credit account configured.")

            credit_line = (0, 0, {
                'account_id': credit_account_id,
                'partner_id': voucher.payee_id.id,
                'name': voucher.purpose or '/',
                'debit': 0.0,
                'credit': voucher.contract_value,
            })

            move_vals['line_ids'] = [debit_line, credit_line]

            move = self.env['account.move'].create(move_vals)
            move.action_post()
            voucher.is_locked = True

            # Optionally: store reference
            # voucher.move_id = move.id

    def compute_journal_count(self):
        for voucher in self:
            count = self.env['account.move'].search_count([('ref', '=', voucher.name)])
            voucher.journal_count = count

    @api.onchange('partner_id')
    def _compute_outstanding_debits(self):
        for record in self:
            if not record.payee_id:
                record.outstanding_debits = 0.0
                continue

            # Determine whether the partner is a vendor or customer based on account type
            # You can improve this logic based on context or your app flow
            account_types = ['liability_payable', 'asset_receivable']  # for vendors and customers

            domain = [
                ('partner_id', '=', record.payee_id.id),
                ('account_id.account_type', 'in', account_types),
                ('move_id.state', '=', 'posted'),
            ]

            move_lines = self.env['account.move.line'].search(domain)

            total_debit = sum(line.debit for line in move_lines)
            total_credit = sum(line.credit for line in move_lines)

            # Positive amount means partner owes company (e.g. vendor to be paid)
            # Negative means company owes partner (e.g. overpayment)
            outstanding = total_debit - total_credit

            record.outstanding_debits = outstanding

    def compute_voucher_count(self):
        for voucher in self:
            count = self.env['payment.voucher.breakdown'].search_count([('voucher_id', '=', voucher.id)])
            voucher.voucher_count = count

    def action_open_voucher(self):
        voucher_ids = self.env['payment.voucher.breakdown'].search([('voucher_id', '=', self.id)])
        return {
            'type': 'ir.actions.act_window',
            'name': 'Payment Voucher Details',
            'res_model': 'payment.voucher.breakdown',
            'view_mode': 'list,form',
            'domain': [('voucher_id', '=', self.id)],
        }

    def action_open_breakdown(self):
        if self.outstanding_debits == 0.0:
            raise UserError("This Vendor or Customer has no outstanding credits.")
        total = self.contract_value or 0.0
        stamp_duty = round(total * 0.01, 2)
        vat = round(total * 0.05, 2)
        wht = round((total - stamp_duty - vat) * 0.05, 2)
        supplier = round(total - stamp_duty - vat - wht, 2)

        breakdown = self.env['payment.voucher.breakdown'].create({
            'voucher_id': self.id,
            'partner_id': self.payee_id.id,
            'amount_to_paid': 0.00,
            'expense_account_id': self.expense_account_id.id,
            'state': 'draft',
        })

        lines = [
            {
                'description': "",
                'debit_amount': 0.00,
                'credit_amount': supplier,
                'currency_id':self.currency_id.id ,
                'account_id': self.expense_account_id.id,
                'account_code': self.expense_account_id.code
            },
            {
                'description': "1% STAMP DUTY",
                'credit_amount': stamp_duty,
                'debit_amount': 0.00,
                'currency_id': self.currency_id.id,
                'account_id': self.env['account.account'].search([('code', '=', '41030102')], limit=1).id,
                'account_code': self.env['account.account'].search([('code', '=', '41030102')], limit=1).code
            },
            {
                'description': "5% VAT",
                'debit_amount': 0.00,
                'credit_amount': vat,
                'currency_id': self.currency_id.id,
                'account_id': self.env['account.account'].search([('code', '=', '41030103')], limit=1).id,
                'account_code': self.env['account.account'].search([('code', '=', '41030103')], limit=1).code
            },
            {
                'description': "5% WHT",
                'debit_amount': 0.00,
                'credit_amount': wht,
                'currency_id': self.currency_id.id,
                'account_id': self.env['account.account'].search([('code', '=', '41030102')], limit=1).id,
                'account_code': self.env['account.account'].search([('code', '=', '41030102')], limit=1).code
            },
            {
                'description': self.payee_id.name,
                'debit_amount': total,
                'credit_amount': 0.00,
                'currency_id': self.currency_id.id,
                'account_id': self.payee_id.property_account_payable_id.id,
                'account_code': self.payee_id.property_account_payable_id.code
            }
        ]

        # for line in lines:
        #     self.env['payment.voucher.breakdown.line'].create({
        #         'breakdown_id': breakdown.id,
        #         'description': line['description'],
        #         'debit_amount': line['debit_amount'],
        #         'credit_amount': line['credit_amount'],
        #         'account_id': line['account_id'],
        #         'currency_id': self.currency_id.id,
        #     })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Payment Breakdown',
            'res_model': 'payment.voucher.breakdown',
            'view_mode': 'form',
            'res_id': breakdown.id,
            'target': 'new',
        }

    def create(self, val):
        if val.get('projects') == 'state':
            code = self.env["ir.sequence"].next_by_code("custom.payment.voucher.state") or "New"
            val["name"] = code
        elif val.get('projects') == 'expenditure':
            code = self.env["ir.sequence"].next_by_code("custom.payment.voucher.expenditure") or "New"
            val["name"] = code
        elif val.get('projects') == 'special':
            code = self.env["ir.sequence"].next_by_code("custom.payment.voucher.special") or "New"
            val["name"] = code
        return super(PaymentVoucher, self).create(val)

    def log_approval(self, action, comment=''):
        # Require comment only if action is 'rejected'
        if action == 'cancel' and not comment:
            raise UserError("You must provide a comment when rejecting a voucher.")

        self.env['approval.log.line'].create({
            'voucher_id': self.id,
            'action': action,
            'comment': comment,
            'user_id': self.env.user.id,
        })

    def open_approval_comment_wizard(self, action_type):
        return {
            'name': 'Enter Comment',
            'type': 'ir.actions.act_window',
            'res_model': 'approval.comment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_voucher_id': self.id,
                'default_action_type': action_type,
            }
        }

    def action_prepare(self):
        return self.open_approval_comment_wizard('prepare')

    def action_cancel(self):
        return self.open_approval_comment_wizard('cancel')

    def unlink(self):
        for rec in self:
            if rec.journal_count > 0:
                raise UserError("You cannot delete a voucher that has a journal entry.")
        return super(PaymentVoucher, self).unlink()