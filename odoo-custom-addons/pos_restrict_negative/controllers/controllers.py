# -*- coding: utf-8 -*-
# from odoo import http

# from odoo import http
# from odoo.http import request
#
#
# class ProductController(http.Controller):
#     @http.route('/get_available_quantity', type='json', auth='user')
#     def get_available_quantity(self, product_id, location_id):
#         product = request.env['product.product'].browse(product_id)
#         quantity = product.get_available_quantity_by_location(product_id, location_id)
#         return {'available_quantity': quantity}

# class PosRestrictNegative(http.Controller):
#     @http.route('/pos_restrict_negative/pos_restrict_negative', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_restrict_negative/pos_restrict_negative/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_restrict_negative.listing', {
#             'root': '/pos_restrict_negative/pos_restrict_negative',
#             'objects': http.request.env['pos_restrict_negative.pos_restrict_negative'].search([]),
#         })

#     @http.route('/pos_restrict_negative/pos_restrict_negative/objects/<model("pos_restrict_negative.pos_restrict_negative"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_restrict_negative.object', {
#             'object': obj
#         })
