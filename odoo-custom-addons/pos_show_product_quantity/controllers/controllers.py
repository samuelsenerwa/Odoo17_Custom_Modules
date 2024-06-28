# -*- coding: utf-8 -*-
# from odoo import http


# class PosShowProductQuantity(http.Controller):
#     @http.route('/pos_show_product_quantity/pos_show_product_quantity', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_show_product_quantity/pos_show_product_quantity/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_show_product_quantity.listing', {
#             'root': '/pos_show_product_quantity/pos_show_product_quantity',
#             'objects': http.request.env['pos_show_product_quantity.pos_show_product_quantity'].search([]),
#         })

#     @http.route('/pos_show_product_quantity/pos_show_product_quantity/objects/<model("pos_show_product_quantity.pos_show_product_quantity"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_show_product_quantity.object', {
#             'object': obj
#         })

