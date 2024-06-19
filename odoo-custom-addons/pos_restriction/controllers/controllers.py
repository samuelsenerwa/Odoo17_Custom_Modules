# -*- coding: utf-8 -*-
# from odoo import http


# class PosRestriction(http.Controller):
#     @http.route('/pos_restriction/pos_restriction', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_restriction/pos_restriction/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_restriction.listing', {
#             'root': '/pos_restriction/pos_restriction',
#             'objects': http.request.env['pos_restriction.pos_restriction'].search([]),
#         })

#     @http.route('/pos_restriction/pos_restriction/objects/<model("pos_restriction.pos_restriction"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_restriction.object', {
#             'object': obj
#         })

