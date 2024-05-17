# -*- coding: utf-8 -*-
# from odoo import http


# class HerenahSalaryAdvance(http.Controller):
#     @http.route('/herenah_salary_advance/herenah_salary_advance', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/herenah_salary_advance/herenah_salary_advance/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('herenah_salary_advance.listing', {
#             'root': '/herenah_salary_advance/herenah_salary_advance',
#             'objects': http.request.env['herenah_salary_advance.herenah_salary_advance'].search([]),
#         })

#     @http.route('/herenah_salary_advance/herenah_salary_advance/objects/<model("herenah_salary_advance.herenah_salary_advance"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('herenah_salary_advance.object', {
#             'object': obj
#         })

