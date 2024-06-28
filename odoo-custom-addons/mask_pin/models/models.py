# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class mask_pin(models.Model):
#     _name = 'mask_pin.mask_pin'
#     _description = 'mask_pin.mask_pin'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

