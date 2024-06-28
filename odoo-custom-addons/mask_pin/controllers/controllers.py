# -*- coding: utf-8 -*-
# from odoo import http


# class MaskPin(http.Controller):
#     @http.route('/mask_pin/mask_pin', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mask_pin/mask_pin/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('mask_pin.listing', {
#             'root': '/mask_pin/mask_pin',
#             'objects': http.request.env['mask_pin.mask_pin'].search([]),
#         })

#     @http.route('/mask_pin/mask_pin/objects/<model("mask_pin.mask_pin"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mask_pin.object', {
#             'object': obj
#         })

