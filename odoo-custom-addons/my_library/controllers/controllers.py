# -*- coding: utf-8 -*-
# from odoo import http


# class MyLibrary(http.Controller):
#     @http.route('/my_library/my_library', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/my_library/my_library/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('my_library.listing', {
#             'root': '/my_library/my_library',
#             'objects': http.request.env['my_library.my_library'].search([]),
#         })

#     @http.route('/my_library/my_library/objects/<model("my_library.my_library"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('my_library.object', {
#             'object': obj
#         })

