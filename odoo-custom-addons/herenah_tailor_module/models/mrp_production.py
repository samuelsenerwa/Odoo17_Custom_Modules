# -*- coding: utf-8 -*-

from odoo import models, fields, api

class herenah_tailor_module(models.Model):
    _inherit = 'mrp.production'
    _description = 'Production Order with a field for tailor and packer'

    tailor_id = fields.Many2many('hr.employee', 'tailor_rel','employee', string='Tailor Straight')
    packer_id = fields.Many2many('hr.employee', 'packer_rel', string='Packer')
    overlock_id = fields.Many2many('hr.employee','overlock_rel', string='Tailor Overlock')
    cutter_id = fields.Many2many('hr.employee', 'cutter_rel', string='Cutter')
    flat_id = fields.Many2many('hr.employee', 'flat_rel', string='Tailor Flat')
    salary_overlock = fields.Integer(string='Overlock Salary')
    salary_flat = fields.Integer(string='Flat Salary')
    salary_straight = fields.Integer(string='Straight Salary')
    salary_packer = fields.Integer(string='Packer Salary')
    salary_cutter = fields.Integer(string='Cutter Salary')
    payment_breakdown = fields.Text(string="Payment Breakdown", required=True)


    # @api.constrains('salary_field')
    # def _check_custom_integer_field(self):
    #     for record in self:
    #         if record.custom_integer_field and not record.custom_integer_field.isdigit():
    #             raise ValidationError("Please enter only integer values for Salary Field!")

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

