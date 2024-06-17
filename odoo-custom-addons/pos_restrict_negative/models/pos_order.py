from odoo import models, fields, api


class pos_order(models.Model):
    _inherit = 'pos.order'

    location_id = fields.Many2one(
        comodel_name='stock.location',
        related='config_id.stock_location_id',
        string="Location", store=True,
        readonly=True,
    )


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
        product_ids = self.env['product.product'].sudo().browse(products)
        for product in product_ids:
            quants = self.env['stock.quant'].sudo().search(
                [('product_id', '=', product.id), ('location_id', '=', location),
                 ('company_id', '=', self.env.user.company_id.id)])
            # , ('company_id', 'in', self._context.allowed_company_ids)
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
        quants = self.env['stock.quant'].search([('product_id', '=', pro.id), ('location_id', '=', location)])
        if len(quants) > 1:
            quantity = 0.0
            for quant in quants:
                quantity += quant.quantity
            res.append([pro.id, quantity])
        else:
            res.append([pro.id, quants.quantity])
        return res


class product(models.Model):
    _inherit = 'product.product'

    available_quantity = fields.Float('Available Quantity')

    def get_stock_location_avail_qty(self, location, products):
        res = {}
        product_ids = self.env['product.product'].browse(products)
        if location:
            for product in product_ids.filtered(lambda x: x.company_id == self.env.user.company_id):
                quants = self.env['stock.quant'].search(
                    [('product_id', '=', product.id), ('location_id', '=', location),
                     ('company_id', '=', self.env.user.company_id.id)])
                outgoing = self.env['stock.move'].search(
                    [('product_id', '=', product.id), ('location_id', '=', location),
                     ('company_id', '=', self.env.user.company_id.id)])
                incoming = self.env['stock.move'].search(
                    [('product_id', '=', product.id), ('location_dest_id', '=', location),
                     ('company_id', '=', self.env.user.company_id.id)])
                qty = 0.0
                product_qty = 0.0
                incoming_qty = 0.0
                if len(quants) > 1:
                    for quant in quants:
                        qty += quant.quantity

                    if len(outgoing) > 0:
                        for quant in outgoing:
                            if quant.state not in ['done']:
                                product_qty += quant.product_qty

                    if len(incoming) > 0:
                        for quant in incoming:
                            if quant.state not in ['done']:
                                incoming_qty += quant.product_qty
                        product.available_quantity = qty - product_qty + incoming_qty
                        res.update({product.id: qty - product_qty + incoming_qty})
                else:
                    if not quants:
                        if len(outgoing) > 0:
                            for quant in outgoing:
                                if quant.state not in ['done']:
                                    product_qty += quant.product_qty

                        if len(incoming) > 0:
                            for quant in incoming:
                                if quant.state not in ['done']:
                                    incoming_qty += quant.product_qty
                        product.available_quantity = qty - product_qty + incoming_qty
                        res.update({product.id: qty - product_qty + incoming_qty})
                    else:
                        if len(outgoing) > 0:
                            for quant in outgoing:
                                if quant.state not in ['done']:
                                    product_qty += quant.product_qty

                        if len(incoming) > 0:
                            for quant in incoming:
                                if quant.state not in ['done']:
                                    incoming_qty += quant.product_qty
                        product.available_quantity = quants.quantity - product_qty + incoming_qty
                        res.update({product.id: quants.quantity - product_qty + incoming_qty})
        return [res]
