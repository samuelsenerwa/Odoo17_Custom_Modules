# -*- coding: utf-8 -*-
# from odoo import http


# class BackdateSaleOrderDate(http.Controller):
#     @http.route('/backdate_sale_order_date/backdate_sale_order_date/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/backdate_sale_order_date/backdate_sale_order_date/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('backdate_sale_order_date.listing', {
#             'root': '/backdate_sale_order_date/backdate_sale_order_date',
#             'objects': http.request.env['backdate_sale_order_date.backdate_sale_order_date'].search([]),
#         })

#     @http.route('/backdate_sale_order_date/backdate_sale_order_date/objects/<model("backdate_sale_order_date.backdate_sale_order_date"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('backdate_sale_order_date.object', {
#             'object': obj
#         })
