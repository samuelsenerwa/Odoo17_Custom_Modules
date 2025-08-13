from odoo import models, fields, api, _

class ApprovalCommentWizard(models.TransientModel):
    _name = 'approval.comment.wizard'
    _description = 'Approval Comment Wizard For Payment Voucher'

    comment = fields.Text(string="Comment", required=True)
    voucher_id = fields.Many2one('payment.voucher', required=True)
    action_type = fields.Selection([('prepare', 'Prepare'), ('cancel', 'Cancel')], required=True)

    def action_confirm(self):
        if self.action_type == 'prepare':
            self.voucher_id.write({
                'state': 'prepared',
                'prepared_by': self.env.user.id,
            })
            self.voucher_id.log_approval('prepared', self.comment)
        elif self.action_type == 'cancel':
            self.voucher_id.write({
                'state': 'cancel',
                'cancelled_by': self.env.user.id,
            })
            self.voucher_id.log_approval('cancel', self.comment)

class VoucherCommentVoucherWizard(models.TransientModel):
    _name = 'approval.comment.wizard.voucher'
    _description = 'Approval Comment Wizard For Voucher Details'

    comment = fields.Text(string="Comment", required=True)
    voucher_id = fields.Many2one('payment.voucher.breakdown', required=True)
    action_type = fields.Selection([
        ('cancel', 'Cancel'),
        ('checked', 'Checked'),
        ('authorized', 'Authorized'),
        ('certified', 'Certified'),
        ('funds_budget', 'Funds & Budget Approved'),
        ('audit', 'Audited'),
        ('cash_office', 'Cash Office Approved'),
        ('done', 'Paid'),
        ('rejected', 'Rejected'),
        ('cancel', 'Cancelled'),
    ], required=True)

    def action_confirm(self):
        if self.action_type == 'checked':
            self.voucher_id.write({
                'state': 'checked',
                'prepared_by': self.env.user.id,
            })
            self.voucher_id.log_approval('checked', self.comment)
        elif self.action_type == 'authorized':
            self.voucher_id.write({
                'state': 'authorized',
                'prepared_by': self.env.user.id,
            })
            self.voucher_id.log_approval('authorized', self.comment)
        elif self.action_type == 'certified':
            self.voucher_id.write({
                'state': 'certified',
                'prepared_by': self.env.user.id,
            })
            self.voucher_id.log_approval('certified', self.comment)

        elif self.action_type == 'funds_budget':
            self.voucher_id.write({
                'state': 'funds_budget',
                'prepared_by': self.env.user.id,
            })
            self.voucher_id.log_approval('funds_budget', self.comment)

        elif self.action_type == 'audit':
            self.voucher_id.write({
                'state': 'audit',
                'cancelled_by': self.env.user.id,
            })
            self.voucher_id.log_approval('audit', self.comment)

        elif self.action_type == 'cash_office':
            self.voucher_id.write({
                'state': 'cash_office',
                'prepared_by': self.env.user.id,
            })
            self.voucher_id.log_approval('cash_office', self.comment)

        elif self.action_type == 'done':
            self.voucher_id.write({
                'state': 'done',
                'prepared_by': self.env.user.id,
            })
            self.voucher_id.log_approval('done', self.comment)

        elif self.action_type == 'rejected':
            self.voucher_id.write({
                'state': 'rejected',
                'prepared_by': self.env.user.id,
            })
            self.voucher_id.log_approval('rejected', self.comment)

        elif self.action_type == 'cancel':
            # we have to rest to draft and then cancel the first journal entry
            for rec in self.voucher_id:
                if rec.journal_entry_id:
                    rec.journal_entry_id.button_draft()
                    rec.journal_entry_id.button_cancel()
                rec.write({
                    'state': 'cancel',
                    'cancelled_by': self.env.user.id,
                })
                rec.voucher_id._update_payment_status()
            self.voucher_id.log_approval('cancel', self.comment)