# -*- coding: utf-8 -*-
# from odoo import http


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

