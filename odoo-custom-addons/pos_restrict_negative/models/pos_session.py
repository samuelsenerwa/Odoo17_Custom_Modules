# pos_session.py
from odoo import models, api, _
import logging

_logger = logging.getLogger(__name__)


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_product_product(self):
        result = super()._loader_params_product_product()
        result['search_params']['fields'].extend(['qty_available', 'type'])
        return result

    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        result.append('product.product')
        return result

    @api.model
    def _get_pos_ui_data(self):
        result = super()._get_pos_ui_data()
        locations = self.env['pos.config'].search([]).mapped('stock_location_id')
        products = self.env['product.product'].search([])
        quantities = self._get_product_quantities(products, locations)
        result.update({
            'product_quantities': quantities,
        })
        _logger.info("Product Quantities: %s", quantities)
        return result

    def _get_product_quantities(self, products, locations):
        quantities = {}
        for product in products:
            quantities[product.id] = {
                location.id: product.with_context(location=location.id).qty_available
                for location in locations
            }
        return quantities
