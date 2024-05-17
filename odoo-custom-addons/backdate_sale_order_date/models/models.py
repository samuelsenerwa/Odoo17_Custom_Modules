 #-*- coding: utf-8 -*-
from odoo import models, fields, api

class sale_order_template(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'
    date_order = fields.Datetime(string='Order Date', required=True, readonly=True, index=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False, help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.")
    
    def _prepare_confirmation_values(self):
        return {
            'state': 'sale'
            }
    
    #@api.multi
    #https://www.odoo.com/es_ES/forum/ayuda-1/odoo-11-difference-between-the-api-multi-and-api-model-decorators-137544?forum=forum.forum%281%2C%29&question=forum.post%28137544%2C%29

    def action_confirm(self):
        res = super().action_confirm()
        #inventory = self.env['ir.module.module'].search([('name', '=', 'inventory')])
        #print("inventory==",inventory);
        for order in self:
            order.commitment_date = order.date_order
            #if inventory:
            picking = self.env['stock.picking'].search([                 
                                ('sale_id', '=',order.id)
                                ])
            if picking:
                for p in picking:                
                    p.scheduled_date = order.date_order 

        return res