# -*- coding: utf-8 -*-

from odoo import models, fields, api


class herenah_salary_advance(models.Model):
    _inherit = 'hr.contract'
    _description = 'herenah salary advance calculation made simple'

    advance_salary = fields.Monetary(string="Advance Salary")
#     _name = 'herenah_salary_advance.herenah_salary_advance'
#     _description = 'herenah_salary_advance.herenah_salary_advance'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
