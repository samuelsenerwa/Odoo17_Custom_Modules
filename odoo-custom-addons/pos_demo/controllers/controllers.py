# -*- coding: utf-8 -*-
# from odoo import http


# class PosDemo(http.Controller):
#     @http.route('/pos_demo/pos_demo', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_demo/pos_demo/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_demo.listing', {
#             'root': '/pos_demo/pos_demo',
#             'objects': http.request.env['pos_demo.pos_demo'].search([]),
#         })

#     @http.route('/pos_demo/pos_demo/objects/<model("pos_demo.pos_demo"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_demo.object', {
#             'object': obj
#         })

