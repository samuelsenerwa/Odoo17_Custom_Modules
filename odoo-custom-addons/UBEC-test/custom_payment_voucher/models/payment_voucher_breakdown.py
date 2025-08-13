from email.policy import default

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PaymentVoucherBreakdown(models.Model):  # or models.Model if you want to persist data
    _name = 'payment.voucher.breakdown'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Payment Voucher Breakdown'

    name = fields.Char(string="Name", required=True, copy=False, readonly=True, default="/")

    payment_date = fields.Date(string="Payment Date", required=True, default=fields.Date.context_today)

    voucher_id = fields.Many2one('payment.voucher', string="Voucher")
    partner_id = fields.Many2one('res.partner', string="Payee", store=True)
    partner_balance_credits = fields.Monetary(string="Balance", currency_field='currency_id', copy=False,
                                              tracking=True, required=True, compute="_compute_outstanding_debits")
    amount_to_paid = fields.Monetary(string="Amount To Be Paid", currency_field='currency_id', copy=False,
                                     tracking=True, help="Enter the amount to be paid to the customer/vendor",
                                     required=True)

    breakdown_line_ids = fields.One2many('payment.voucher.breakdown.line', 'breakdown_id', string="Breakdown Lines")

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='company_id.currency_id',
        readonly=True
    )
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('prepared', 'Prepared'),
        ('checked', 'Checked'),
        ('authorized', 'Authorized'),
        ('certified', 'Certified'),
        ('funds_budget', 'Funds & Budget Approved'),
        ('audit', 'Audited'),
        ('cash_office', 'Cash Office Approved'),
        ('done', 'Paid'),
        ('rejected', 'Rejected'),
        ('cancel', 'Cancelled'),
    ], string="Status", default="draft", tracking=True)

    approval_log_ids = fields.One2many('approval.log.line.voucher', 'voucher_id', string="Approval Log")
    journal_id = fields.Many2one('account.journal', string="Journal", help="Select the Jornal for the Payment Voucher",
                                 default=lambda self: self.env['account.journal'].search(
                                     [('type', 'in', ['cash', 'bank'])], limit=1))
    journal_count = fields.Integer(compute="compute_journal_count", string="Journal Items", copy=False)
    journal_entry_id = fields.Many2one('account.move', string="Journal Items", copy=False)

    expense_account_id = fields.Many2one('account.account', string="Expense Account",
                                         domain=[('account_type', '=', 'expense')], copy=False, tracking=True,
                                         required=True)

    prepared_by = fields.Many2one('res.users', string="Prepared By", tracking=True,
                                  help="This field is used to record the user who prepared the voucher")
    checked_by = fields.Many2one('res.users', string="Checked By", tracking=True)
    cancelled_by = fields.Many2one('res.users', string="Cancelled By",
                                   help="This field is used to record the user who cancelled the voucher",
                                   tracking=True)
    is_locked = fields.Boolean(string='Locked',default=False, copy=False)
    voucher_ref = fields.Char(related='voucher_id.voucher_ref', string="Voucher Ref", copy=False)
    file_no = fields.Char(related='voucher_id.file_no', string="File No", copy=False)

    @api.onchange('breakdown_line_ids')
    def _onchange_balance_lines(self):
        for rec in self:
            total_debit = 0
            total_credit = 0
            balance_line = None
            # Identify existing balance line (optional strategy: last one)
            for line in rec.breakdown_line_ids:
                if not line.account_id:  # Assume empty account used as balance line
                    balance_line = line
                else:
                    total_debit += line.debit_amount
                    total_credit += line.credit_amount
            difference = total_debit - total_credit

            if abs(difference) > 0.001 and balance_line:
                # Apply balancing logic to existing balance line only
                if difference < 0:
                    # Credit is more, balance with debit
                    balance_line.debit_amount = abs(difference)
                    balance_line.credit_amount = 0.0
                else:
                    # Debit is more, balance with credit
                    balance_line.debit_amount = 0.0
                    balance_line.credit_amount = abs(difference)

    def action_lock(self):
        for rec in self:
            rec.is_locked = True

    def action_unlock(self):
        for rec in self:
            rec.is_locked = False

    def write(self, vals):
        if 'amount_to_paid' in vals:
            if vals['amount_to_paid'] > 0:
                # ➤ Validation 2: Debit and Credit Balancing Check
                if 'breakdown_line_ids' in vals:
                    total_debit = 0.0
                    total_credit = 0.0
                    for line in vals['breakdown_line_ids']:
                        if line[0] in (0, 1):  # Create or update
                            data = line[2]
                            total_debit += data.get('debit_amount', 0.0)
                            total_credit += data.get('credit_amount', 0.0)
                    if round(total_debit, 2) != round(total_credit, 2):
                        raise UserError(
                            "Debit and Credit amounts are not balanced. Please correct them before proceeding.")

                # Convert to absolute value to handle negative partner_balance_credits
                outstanding_balance = abs(self.partner_balance_credits)
                if vals['amount_to_paid'] > outstanding_balance:
                    extra_amount = vals['amount_to_paid'] - outstanding_balance
                    raise UserError(
                        f"Amount to be paid cannot be greater than outstanding balance ({outstanding_balance}). "
                        f"You are trying to pay {vals['amount_to_paid']}, which is {extra_amount} more."
                    )
                vals['state'] = 'draft'
            else:
                raise UserError("Amount to be paid cannot be zero or negative.")
        return super(PaymentVoucherBreakdown, self).write(vals)

    def print_voucher(self):
        for rec in self:
            return self.env.ref('custom_payment_voucher.action_report_custom_payment_voucher').report_action(self)
        return None

    def send_email(self):
        self.ensure_one()  # Ensure we're working with a single record
        # ➤ Validation 1: Amount to be paid check
        if self.amount_to_paid <= 0:
            raise UserError("Amount to be paid cannot be zero.")
        # ➤ Validation 2: Debit and Credit Balancing Check
        total_debit = sum(line.debit_amount for line in self.breakdown_line_ids)
        total_credit = sum(line.credit_amount for line in self.breakdown_line_ids)
        if round(total_debit, 2) != round(total_credit, 2):
            raise UserError("Debit and Credit amounts are not balanced. Please correct them before proceeding.")
        # ➤ Proceed to prepare and send email
        self.write({
            'state': 'prepared',
            'prepared_by': self.env.user.id,
            'is_locked': True
        })
        self.action_email('group_payment_voucher_checker')

    def get_base_url(self):
        self.ensure_one()  # Ensures it's a singleton
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return f"{base_url}/odoo/{self._name}/{self.id}"

    def action_email(self, email_group):
        self.ensure_one()
        template = self.env.ref('custom_payment_voucher.email_template_payment_voucher_notify')
        # Dynamically build the full external ID of the group
        group_xml_id = f'custom_payment_voucher.{email_group}'
        approver_group = self.env.ref(group_xml_id, raise_if_not_found=False)
        if not approver_group:
            raise ValueError(f"Group '{email_group}' not found.")
        users = self.env['res.users'].search([('groups_id', 'in', approver_group.id)])
        for user in users:
            if user.partner_id.email:
                template.send_mail(self.id, force_send=True, email_values={'email_to': user.partner_id.email})

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

    def compute_journal_count(self):
        for voucher in self:
            count = self.env['account.move'].search_count([('ref', '=', voucher.name)])
            voucher.journal_count = count

    # @api.onchange('amount_to_paid')
    # def _onchange_amount_to_paid(self):
    #     for rec in self:
    #         total = rec.amount_to_paid or 0.0
    #         stamp_duty = round(total * 0.01, 2)
    #         vat = round(total * 0.05, 2)
    #         wht = round((total - stamp_duty - vat) * 0.05, 2)
    #         supplier = round(total - stamp_duty - vat - wht, 2)
    #
    #         # Clear previous lines
    #         rec.breakdown_line_ids = [(5, 0, 0)]  # Remove all existing lines
    #
    #         # Recreate lines
    #         rec.breakdown_line_ids = [(0, 0, {
    #             'description': "",
    #             'debit_amount': 0.00,
    #             'credit_amount': supplier,
    #             'account_id': rec.expense_account_id.id
    #         }), (0, 0, {
    #             'description': "1% STAMP DUTY",
    #             'debit_amount': 0.0,
    #             'credit_amount': stamp_duty,
    #             'account_id': self.env['account.account'].search([('code', '=', '41030102')], limit=1).id
    #         }), (0, 0, {
    #             'description': "5% VAT",
    #             'debit_amount': 0.0,
    #             'credit_amount': vat,
    #             'account_id': self.env['account.account'].search([('code', '=', '41030103')], limit=1).id
    #         }), (0, 0, {
    #             'description': "5% WHT",
    #             'debit_amount': 0.0,
    #             'credit_amount': wht,
    #             'account_id': self.env['account.account'].search([('code', '=', '41030102')], limit=1).id
    #         }), (0, 0, {
    #             'description': rec.partner_id.name,
    #             'debit_amount': total,
    #             'credit_amount': 0.00,
    #             'account_id': rec.partner_id.property_account_payable_id.id
    #         })]

    def log_approval(self, action, comment=''):
        # Require comment only if action is 'rejected'
        if action in ['cancel', 'rejected'] and not comment:
            raise UserError("You must provide a comment when rejecting a voucher.")
        self.env['approval.log.line.voucher'].create({
            'voucher_id': self.id,
            'action': action,
            'comment': comment,
            'user_id': self.env.user.id,
        })
        if action == 'checked':
            self.action_email('group_payment_voucher_authorizer')
        elif action == 'authorized':
            self.action_email('group_payment_voucher_certifier')
        elif action == 'certified':
            self.action_email('group_payment_voucher_funds_budget')
        elif action == 'funds_budget':
            self.action_email('group_payment_voucher_auditor')
        elif action == 'audit':
            self.action_email('group_payment_voucher_cash_office')

    @api.onchange('partner_id')
    def _compute_outstanding_debits(self):
        for record in self:
            if not record.partner_id:
                record.partner_balance_credits = 0.0
                continue

            # Determine whether the partner is a vendor or customer based on account type
            # You can improve this logic based on context or your app flow
            account_types = ['liability_payable', 'asset_receivable']  # for vendors and customers

            domain = [
                ('partner_id', '=', record.partner_id.id),
                ('account_id.account_type', 'in', account_types),
                ('move_id.state', '=', 'posted'),
            ]

            move_lines = self.env['account.move.line'].search(domain)

            total_debit = sum(line.debit for line in move_lines)
            total_credit = sum(line.credit for line in move_lines)

            # Positive amount means partner owes company (e.g. vendor to be paid)
            # Negative means company owes partner (e.g. overpayment)
            outstanding = total_debit - total_credit

            record.partner_balance_credits = outstanding

    @api.model
    def create(self, val):
        if val.get("name", "/") == "/":
            voucher = val.get('voucher_id')
            vouchers = self.env['payment.voucher'].search([('id', '=', voucher)])
            if vouchers.projects == 'special':
                seq = self.env["ir.sequence"].search([('code', '=', 'custom.payment.voucher.special')])
                prefix = seq.prefix
                code = self.env["ir.sequence"].next_by_code("payment.breakdown.voucher") or "New"
                val["name"] = prefix + code
            elif vouchers.projects == 'expenditure':
                seq = self.env["ir.sequence"].search([('code', '=', 'custom.payment.voucher.expenditure')])
                prefix = seq.prefix
                code = self.env["ir.sequence"].next_by_code("payment.breakdown.voucher") or "New"
                val["name"] = prefix + code
            elif vouchers.projects == 'state':
                seq = self.env["ir.sequence"].search([('code', '=', 'custom.payment.voucher.state')])
                prefix = seq.prefix
                code = self.env["ir.sequence"].next_by_code("payment.breakdown.voucher") or "New"
                val["name"] = prefix + code
        # Create the record
        record = super(PaymentVoucherBreakdown, self).create(val)
        # # Now send the email (assuming group name is correct)
        # record.action_email('group_payment_voucher_checker')
        return record

    def open_approval_comment_wizard(self, action_type):
        return {
            'name': 'Enter Comment',
            'type': 'ir.actions.act_window',
            'res_model': 'approval.comment.wizard.voucher',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_voucher_id': self.id,
                'default_action_type': action_type,
            }
        }

    def action_check(self):
        return self.open_approval_comment_wizard('checked')

    def action_authorize(self):
        return self.open_approval_comment_wizard('authorized')

    def action_certify(self):
        return self.open_approval_comment_wizard('certified')

    def action_funds_budget(self):
        return self.open_approval_comment_wizard('funds_budget')

    def action_audit(self):
        return self.open_approval_comment_wizard('audit')

    def action_cash_office(self):
        return self.open_approval_comment_wizard('cash_office')

    def action_reject(self):
        return self.open_approval_comment_wizard('rejected')

    def action_cancel(self):
        #for rec in self:
            # if rec.journal_entry_id:
            #     rec.journal_entry_id.button_draft()
            #     rec.journal_entry_id.button_cancel()
        return self.open_approval_comment_wizard('cancel')

    def action_paid(self):
        for rec in self:
            if not rec.journal_id:
                raise UserError("Please select a Journal before posting.")
            if not rec.breakdown_line_ids:
                raise UserError("Breakdown lines are missing.")

            total_debit_sum = sum(line.debit_amount for line in rec.breakdown_line_ids)
            total_credit_sum = sum(line.credit_amount for line in rec.breakdown_line_ids)

            if round(total_debit_sum, 2) != round(total_credit_sum, 2):
                raise UserError(
                    f"Debit ({total_debit_sum:.2f}) and Credit ({total_credit_sum:.2f}) are not balanced. "
                    "Please correct the breakdown lines."
                )

            line_vals = []
            for line in rec.breakdown_line_ids:
                if not line.account_id:
                    raise UserError(f"Missing account in breakdown line: {line.description}")

                line_vals.append((0, 0, {
                    'name': line.description or '/',
                    'account_id': line.account_id.id,
                    'debit': line.debit_amount,
                    'credit': line.credit_amount,
                    'partner_id': rec.partner_id.id,
                }))

            move_vals = {
                'journal_id': rec.journal_id.id,
                'date': rec.payment_date,
                'ref': rec.name,
                'move_type': 'entry',
                'line_ids': line_vals,
            }

            # Step 1: Create and post journal entry
            move = self.env['account.move'].create(move_vals)
            move.action_post()

            # Flush to ensure move.id is written to the DB
            # self.env.cr.flush()
            # self.env.cr.commit()
            rec.state = 'done'

            # Step 2: Now safely assign values and update state
            rec.journal_entry_id = move.id
            rec.voucher_id._update_payment_status()

    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise UserError("You cannot delete a voucher that has a journal entry.")
        return super(PaymentVoucherBreakdown, self).unlink()


class PaymentVoucherBreakdownLine(models.Model):  # or models.Model
    _name = 'payment.voucher.breakdown.line'
    _description = 'Breakdown Line'

    breakdown_id = fields.Many2one('payment.voucher.breakdown', string="Breakdown")
    description = fields.Char(string="Description")
    account_id = fields.Many2one('account.account', string="Account")
    account_code = fields.Char(string="Account Code", compute="compute_acc_code")

    debit_amount = fields.Monetary(string="Debit", currency_field='currency_id')
    credit_amount = fields.Monetary(string="Credit", currency_field='currency_id')

    currency_id = fields.Many2one('res.currency', string="Currency")

    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account'
    )

    @api.onchange('account_id')
    def compute_acc_code(self):
        for rec in self:
            if rec.account_id:
                rec.account_code = rec.account_id.code
            else:
                rec.account_code = ''

    def unlink(self):
        for record in self:
            if record.breakdown_id.state != 'draft':
                raise UserError("You cannot delete lines when the voucher is not in draft state.")
        return super(PaymentVoucherBreakdownLine, self).unlink()

    # @api.onchange('debit_amount', 'credit_amount')
    # def _onchange_auto_balance(self):
    #     for rec in self:
    #         if not rec.breakdown_id or len(rec.breakdown_id.breakdown_line_ids) != 2:
    #             return  # Only apply when there are exactly 2 lines
    #         # Get the other line
    #         other_lines = rec.breakdown_id.breakdown_line_ids.filtered(lambda l: l.id != rec.id)
    #         if not other_lines:
    #             return
    #         other_line = other_lines[0]
    #         # If current line has debit, set credit on the other
    #         if other_line.debit_amount and not other_line.credit_amount:
    #             other_line.credit_amount = other_line.debit_amount
    #             other_line.debit_amount = 0.0
    #         elif other_line.credit_amount and not other_line.debit_amount:
    #             other_line.debit_amount = other_line.credit_amount
    #             other_line.credit_amount = 0.0
