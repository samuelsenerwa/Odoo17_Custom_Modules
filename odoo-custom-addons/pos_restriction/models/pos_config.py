# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PosConfig(models.Model):
    _inherit = "pos.config"

    def _get_default_location(self):
        return self.env['stock.warehouse'].search([('company_id', '=', self.env.user.company_id.id)],
                                                  limit=1
                                                  ).lot_stock_id

    restrict_zero_qty = fields.Boolean(string="Restrict Zero Quantity")

    pos_stock_type = fields.Selection(
        [('onhand', 'Qty on Hand'), ('incoming', 'Incoming Qty'), ('outgoing', 'Outgoing Qty'),
         ('available', 'Qty Available')], string='Stock Type', help='Seller can display Different stock type in POS.'
    )

    stock_location_id = fields.Many2one(
        'stock.location', string='Stock Location',
        domain=[('usage', '=', 'internal')], required=True, default=_get_default_location)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    restrict_zero_qty = fields.Boolean(related="pos_config_id.restrict_zero_qty", readonly=False)
    pos_stock_type = fields.Selection(related="pos_config_id.pos_stock_type", readonly=False)
    stock_location_id = fields.Many2one(
        related='pos_config_id.stock_location_id',
        comodel_name='stock.location',
        string='Stock Location',
        readonly=False
    )


class pos_order(models.Model):
    _inherit = "pos.order"

    location_id = fields.Many2one(
        comodel_name='stock.location',
        related='config_id.stock_location_id',
        string="Location", store=True,
        readonly=True,
    )


# determine the stock from all the locations existing in the system
class stock_quant(models.Model):
    _inherit = 'stock.quant'

    def get_stock_location_qty(self, location):
        res = {}
        product_ids = self.env['product.product'].search([])
        for product in product_ids:
            quants = self.env['stock.quant'].search(
                [('product_id', '=', product.id), ('location_id', '=', location['id']),
                 ('company_id', '=', self.env.user.company_id.id)])
            if len(quants) > 1:
                quantity = 0.0
                for quant in quants:
                    quantity += quant.quantity
                res.update({product.id: quantity})
            else:
                res.update({product.id: quants.quantity})
        return [res]

    def get_products_stock_location_qty(self, location, products):
        res = {}
        product_ids = self.env['product.product'].browse(products)
        for product in product_ids:
            quants = self.env['stock.quant'].search(
                [('product_id', '=', product.id), ('location_id', '=', location),
                 ('company_id', '=', self.env.user.company_id.id)])
            if len(quants) > 1:
                quantity = 0.0
                for quant in quants:
                    quantity += quant.quantity
                res.update({product.id: quantity})
            else:
                res.update({product.id: quants.quantity})
        return [res]

    def get_single_product(self, product, location):
        res = []
        pro = self.env['product.product'].browse(product)
        quants = self.env['stock.quant'].search([('product_id', '=', pro.id), ('location', '=', location)])
        if len(quants) > 1:
            quantity = 0.0
            for quant in quants:
                quantity += quant.quantity
            res.append([pro.id, quantity])
        else:
            res.append([pro.id, quants.quantity])
        return res


# calculate the on hand quantity and available quantity
class product(models.Model):
    _inherit = 'product.product'

    quantity_on_hand = fields.Float('Quantity on Hand')
    available_quantity = fields.Float('Available Quantity')

    def get_stock_location_avail_qty(self, location, products):
        res = {}
        product_ids = self.env['product.product'].browse(products)
        if location:
            for product in product_ids.filtered(lambda x: x.company_id == self.env.user.company_id):
                quants = self.env['stock_quant'].search(
                    [('product_id', '=', product.id),
                     ('location_id', '=', location),
                     ('company_id', '=', self.env.user.company_id.id)
                     ])

                qty = sum(quants.mapped('quantity'))

                product.quantity_on_hand = qty
                # product.available_quantity = qty
                res.update({product.id: qty})

        return [res]
