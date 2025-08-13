from odoo import models, fields

class ApprovalLogLine(models.Model):
    _name = 'approval.log.line'
    _description = 'Approval Log Line'

    voucher_id = fields.Many2one('payment.voucher', string="Voucher", ondelete="cascade")
    record_id = fields.Many2one('payment.voucher.breakdown', string="Voucher", ondelete="cascade")
    action = fields.Selection([
        ('prepared', 'Prepared'),
        ('cancel', 'Cancelled'),
    ], string="Action")

    comment = fields.Text(string="Comment")

    user_id = fields.Many2one('res.users', string="Performed By", default=lambda self: self.env.user)
    date = fields.Datetime(string="Date", default=fields.Datetime.now)

class ApprovalLogLinevoucher(models.Model):
    _name = 'approval.log.line.voucher'
    _description = 'Approval Log Line for voucher'


    voucher_id = fields.Many2one('payment.voucher.breakdown', string="Voucher", ondelete="cascade")
    action = fields.Selection([
        ('checked', 'Checked'),
        ('authorized', 'Authorized'),
        ('certified', 'Certified'),
        ('funds_budget', 'Funds & Budget Approved'),
        ('audit', 'Audited'),
        ('cash_office', 'Cash Office Approved'),
        ('done', 'Paid'),
        ('rejected', 'Rejected'),
        ('cancel', 'Cancelled'),
    ], string="Action")

    comment = fields.Text(string="Comment")

    user_id = fields.Many2one('res.users', string="Performed By", default=lambda self: self.env.user)
    date = fields.Datetime(string="Date", default=fields.Datetime.now)
