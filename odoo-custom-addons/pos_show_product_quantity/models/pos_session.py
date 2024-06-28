# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PosSession(models.Model):
    _inherit = "pos.session"

    def _loader_params_product_product(self):
        result = super()._loader_params_product_product()
        result['search_params']['fields'].extend(['qty_available', 'type'])
        return result

    def _get_pos_ui_product_product(self, params):
        products = super()._get_pos_ui_product_product(params)
        picking_type = self.config_id.picking_type_id
        location_id = picking_type.default_location_src_id.id
        for product in products:
            pp = self.env['product.product'].browse([product.get('id')])
            product_qtys = pp.with_context(location=location_id)._compute_quantities_dict(None, None, None, None, None)
            for pos_product in product_qtys:
                product['pos_qty_available'] = product_qtys.get(pos_product).get('qty_available')
        return products
