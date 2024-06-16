# pos_config.py
from odoo import models, fields, api


class PosConfig(models.Model):
    _inherit = "pos.config"

    restrict_zero_qty = fields.Boolean(string='Restrict Zero Quantity')
    stock_location_id = fields.Many2one(
        'stock.location', string='Stock Location',
        domain=[('usage', '=', 'internal')],
        help="Specify the stock location for this POS session."
    )


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    restrict_zero_qty = fields.Boolean(related="pos_config_id.restrict_zero_qty", readonly=False)
    stock_location_id = fields.Many2one(
        related='pos_config_id.stock_location_id',
        comodel_name='stock.location',
        string='Stock Location',
        readonly=False
    )

# from odoo import api, fields, models
# import logging
#
# _logger = logging.getLogger(__name__)
#
#
# class PosConfig(models.Model):
#     _inherit = "pos.config"
#
#     restrict_zero_qty = fields.Boolean(string='Restrict Zero Quantity')
#     stock_location_id = fields.Many2one(
#         'stock.location', string='Stock Location',
#         domain=[('usage', '=', 'internal')],
#         help="Specify the stock location for this POS session."
#     )
#
#
# class ResConfigSettings(models.TransientModel):
#     _inherit = 'res.config.settings'
#
#     restrict_zero_qty = fields.Boolean(related="pos_config_id.restrict_zero_qty", readonly=False)
#     stock_location_id = fields.Many2one(
#         related='pos_config_id.stock_location_id',
#         comodel_name='stock.location',
#         string='Stock Location',
#         readonly=False
#     )
# class PosSession(models.Model):
#     _inherit = 'pos.session'
#
#     def _loader_params_product_product(self):
#         result = super()._loader_params_product_product()
#         result['search_params']['fields'].extend(['qty_available', 'type'])
#         return result

# def _pos_ui_models_to_load(self):
#     result = super()._pos_ui_models_to_load()
#     result.append('pos.location.product.quantity')
#     return result

# @api.model
# def _get_pos_ui_data(self):
#     result = super()._get_pos_ui_data()
#     locations = self.env['pos.session'].search([]).mapped('config_id.stock_location_id')
#     products = self.env['product.product'].search([])
#     quantities = self.env['pos.location.product.quantity'].get_product_quantities(products, locations)
#     result.update({
#         'product_quantities': quantities,
#     })
#     return result


# class PosLocationProductQuantity(models.Model):
#     _name = 'pos.location.product.quantity'
#     _description = 'Product Quantity per Location'
#
#     def get_product_quantities(self, products, locations):
#         quantities = {}
#         for product in products:
#             quantities[product.id] = {location.id: product.with_context(location=location.id).qty_available for location
#                                       in locations}
#         return quantities
