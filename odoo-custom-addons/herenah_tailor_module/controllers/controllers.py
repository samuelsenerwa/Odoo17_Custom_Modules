# -*- coding: utf-8 -*-
# from odoo import http


# class HerenahTailorModule(http.Controller):
#     @http.route('/herenah_tailor_module/herenah_tailor_module', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/herenah_tailor_module/herenah_tailor_module/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('herenah_tailor_module.listing', {
#             'root': '/herenah_tailor_module/herenah_tailor_module',
#             'objects': http.request.env['herenah_tailor_module.herenah_tailor_module'].search([]),
#         })

#     @http.route('/herenah_tailor_module/herenah_tailor_module/objects/<model("herenah_tailor_module.herenah_tailor_module"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('herenah_tailor_module.object', {
#             'object': obj
#         })

