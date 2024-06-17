# pos_config.py
from odoo import models, fields, api


class PosConfig(models.Model):
    _inherit = "pos.config"

    restrict_zero_qty = fields.Boolean(string='Restrict Zero Quantity')

    pos_stock_type = fields.Selection(
        [('onhand', 'Qty on Hand'), ('incoming', 'Incoming Qty'), ('outgoing', 'Outgoing Qty'),
         ('available', 'Qty Available')], string='Stock Type', help='Seller can display Different stock type in POS.')

    stock_location_id = fields.Many2one(
        'stock.location', string='Stock Location',
        domain=[('usage', '=', 'internal')],
        help="Specify the stock location for this POS session."
    )


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    restrict_zero_qty = fields.Boolean(related="pos_config_id.restrict_zero_qty", readonly=False)
    pos_stock_type = fields.Selection(related="pos_config_id.pos_stock_type", readonly=False)
    stock_location_id = fields.Many2one(
        related='pos_config_id.stock_location_id',
        comodel_name='stock.location',
        string='Stock Location',
        readonly=False
    )
