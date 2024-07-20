# -*- coding: utf-8 -*-
# from openerp import models, fields, api, _
# from openerp.exceptions import UserError, AccessError
# from openerp.exceptions import Warning

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError
# from odoo.exceptions import Warning

class HrEquipmentRequest(models.Model):
    _inherit = 'maintenance.request' #inherit maintenance request module

    def _get_picking_in_custom(self):
        pick_in = self.env.ref('stock.picking_type_in', raise_if_not_found=False)
        company = self.env.company
        if not pick_in or pick_in.sudo().warehouse_id.company_id.id != company.id:
            pick_in = self.env['stock.picking.type'].search(
                [('warehouse_id.company_id', '=', company.id), ('code', '=', 'incoming')],
                limit=1,
            )
        return pick_in

    @api.model
    def _get_equipment_picking_type(self):
        type_obj = self.env['stock.picking.type']
        # company_id = self.env.context.get('company_id') or self.env.user.company_id.id
        company_id = self.company_id.id or self.env.user.company_id.id
        #types = type_obj.search([('code', '=', 'internal'), ('warehouse_id.company_id', '=', company_id),])
        types = type_obj.search([('code', '=', 'internal'),('company_id', '=', company_id)])
        return types[0].id if types else False

    @api.model
    def _get_picking_type(self):
        type_obj = self.env['stock.picking.type']
        # company_id = self.env.context.get('company_id') or self.env.user.company_id.id
        company_id = self.company_id.id or self.env.user.company_id.id
        #types = type_obj.search([('code', '=', 'internal'), ('warehouse_id.company_id', '=', company_id),])
        types = type_obj.search([('code', '=', 'internal'),('company_id', '=', company_id)])
        return types[0].id if types else False

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        self.custom_location_id = self.employee_id.department_id.custom_location_id.id

    custom_need_po = fields.Boolean(string="Need PO",help="Tick this box if you want to create Purchase Request", defaults=False)
    custom_need_move = fields.Boolean(string="Need Move",help="Tick this box if you want to create Move", defaults=False)
    custom_equipment_line1 = fields.One2many('equipment.parts.line','request_id1', 'Equipment Parts line')
    custom_equipment_line2 = fields.One2many('equipment.parts.line','request_id2', 'Equipment Parts line')
    custom_needed_parts = fields.One2many('equipment.parts.line','request_id3', 'Needed Parts')
    custom_location_id = fields.Many2one('stock.location','Department Location')
    custom_source_location_id = fields.Many2one('stock.location','Source Location for Internal Move')
    maintenance_picking_type_id = fields.Many2one(
        'stock.picking.type',
        'Maintenance Picking Type',
        default=_get_picking_type,
    )
    custom_maintainer_location_id = fields.Many2one('stock.location','Equipment Repair Location')
    custom_move_done = fields.Boolean()
    custom_po_done = fields.Boolean()
    product_id = fields.Many2one(
        'product.product',
        'Equipment Product'
    )
    equipment_picking_type_id = fields.Many2one(
        'stock.picking.type',
        'Equipment Picking Type',
        default=_get_equipment_picking_type,

    )
    purchase_picking_type_id = fields.Many2one(
        'stock.picking.type', 
        'Purchase Picking Type',
        default=_get_picking_in_custom
    )


    def parts_operation(self):
        po = []
        transfer = []
        for need_parts in self.custom_needed_parts:
            if need_parts.product_stock > 0:
                if need_parts.qty > need_parts.product_stock:
                    if need_parts.compute_done == False:
                        po.append((0,False,{'product_id':need_parts.product_id.id,
                                        'qty':need_parts.qty - need_parts.product_stock}))
                        transfer.append((0,False,{'product_id':need_parts.product_id.id,
                                        'qty':need_parts.product_stock}))
                        need_parts.compute_done = True
                        
                if need_parts.qty < need_parts.product_stock:
                    if need_parts.compute_done == False:
                        transfer.append((0,False,{'product_id':need_parts.product_id.id,
                                        'qty':need_parts.qty}))
                        need_parts.compute_done = True
                    
            if need_parts.product_stock <= 0:
                if need_parts.compute_done == False:
                    po.append((0,False,{'product_id':need_parts.product_id.id, 'qty':need_parts.qty}))
                    need_parts.compute_done = True
        self.custom_equipment_line1 = po
        self.custom_equipment_line2 = transfer
        return True

    # @api.multi #odoo13
    def create_purchase_requisition(self):
        partlist = []
        
        for line in self.custom_equipment_line1:
            if not line.compute_done:
                partlist.append((0,False,{
                    'product_id':line.product_id.id,
                    'product_qty':line.qty,
                    'product_uom_id':line.product_id.uom_id.id,
                    'schedule_date':fields.Date.context_today(self),
                }))
                line.compute_done = True 
        if not partlist:
            raise UserError(_('Purchase requisition is already created!'))
        if partlist:
            if not self.purchase_picking_type_id.id:
                raise UserError(_('Please Select Purchase Picking Type!'))
            create_id = self.env['purchase.requisition'].create(
                {
                    'line_ids':partlist,
                    # 'exclusive':'multiple', 
                    'origin':self.name,
                    'custom_equipment_request_id':self.id, 
                    'description':self.name,
                    'picking_type_id': self.purchase_picking_type_id.id,
                })


    @api.model
    def _get_warehouse(self):
        warehouse = self.env['stock.warehouse'].search([('partner_id','=',self.env.user.company_id.partner_id.id)])
        return warehouse[0].id if warehouse else False

    @api.model
    def _get_company_location(self):
        try:
            location_id = self.env['ir.model.data'].get_object_reference('stock', 'stock_location_stock')[1]
            self.env['stock.location'].check_access_rule('read')
        except (AccessError, ValueError):
            location_id = False
        return location_id

    

    @api.model
    def _prepare_picking_equipment(self):
        # if self._get_picking_type() == False:
        if not self.maintenance_picking_type_id:
            raise UserError(_('Please setup Picking Type.'))
        if not self.custom_maintainer_location_id:
            raise UserError(_("Please choose Maintainer Location."))
        if not self.custom_location_id:
            raise UserError(_("Please select Department Location."))
        return {
            'picking_type_id': self.equipment_picking_type_id.id,
            'partner_id': self.user_id.id,
            'date': fields.date.today(),
            'origin': self.name,
            'location_id': self.custom_location_id.id,
            'location_dest_id': self.custom_maintainer_location_id.id,
            'custom_equipment_request_id':self.id,
        }

    # @api.multi #odoo13
    def _crete_move_line_equipment(self):
        lines = []
        if not self.product_id:
            raise UserError(_('Product Should not be empty.'))
        template = {
            'name': self.name or '',
            'product_id': self.product_id.id,
            'product_uom_qty': 1,
            'product_uom': self.product_id.uom_id.id,
            'date': fields.date.today(),
            'date_deadline': self.request_date,
            'location_id': self.custom_location_id.id,
            'location_dest_id': self.custom_maintainer_location_id.id,
            'partner_id': self.user_id.id,
            'state': 'draft',
            'purchase_line_id': False,
            'company_id': self.env.user.company_id.id,
            'price_unit': self.product_id.standard_price,
            # 'picking_type_id': self._get_picking_type(),
            'picking_type_id': self.equipment_picking_type_id.id,
            'group_id': False,
            'origin': self.name,
            'route_ids': False,
            'warehouse_id':self._get_warehouse(),
        }   
        lines.append(template)
        return lines

    # @api.multi #odoo13
    def create_equipment_move_custom(self):
        for order in self:
            moves = self._crete_move_line_equipment()
            res = order._prepare_picking_equipment()
            if not moves:
                raise UserError(_('Moves are already created.'))
            if moves:
                picking = self.env['stock.picking'].create(res)
                for val in moves:
                    val.update({'picking_id': picking.id})
                    self.env['stock.move'].create(val)
        return True

    @api.model
    def _prepare_picking(self):
        # if self._get_picking_type() == False:
        if not self.maintenance_picking_type_id:
            raise UserError(_('Please setup Picking Type.'))
        if not self.custom_maintainer_location_id:
            raise UserError(_("Please choose Maintainer Location"))
        if not self.custom_source_location_id:
            raise UserError(_("Please select Source Location."))
        return {
            # 'picking_type_id': self._get_picking_type(),
            'picking_type_id': self.maintenance_picking_type_id.id,
            'partner_id': self.user_id.id,
            'date': self.request_date,
            'origin': self.name,
            # 'location_id': self._get_company_location(),
            'location_id': self.custom_source_location_id.id,
            'location_dest_id': self.custom_maintainer_location_id.id,
            'custom_equipment_request_id':self.id,
        }

    # @api.multi #odoo13
    def _crete_move_line(self):
        lines = []
        for line in self.custom_equipment_line2:
            if not line.compute_done:
                template = {
                    'name': self.name or '',
                    'product_id': line.product_id.id,
                    'product_uom_qty':line.qty,
                    'product_uom': line.product_id.uom_id.id,
                    'date': self.request_date,
                    'date_deadline': self.request_date,
                    # 'date_expected': self.request_date,
                    # 'location_id': self._get_company_location(),
                    'location_id': self.custom_source_location_id.id,
                    'location_dest_id': self.custom_maintainer_location_id.id,
                    #'picking_id': picking.id,
                    'partner_id': self.user_id.id,
                    # 'move_dest_id': False,
                    'state': 'draft',
                    'purchase_line_id': False,
                    'company_id': self.env.user.company_id.id,#line.order_id.company_id.id,
                    'price_unit': line.product_id.standard_price,
                    # 'picking_type_id': self._get_picking_type(),
                    'picking_type_id': self.maintenance_picking_type_id.id,
                    'group_id': False,
                    # 'procurement_id': False,
                    'origin': self.name,
                    'route_ids': False,#line.order_id.picking_type_id.warehouse_id and [(6, 0, [x.id for x in line.order_id.picking_type_id.warehouse_id.route_ids])] or [],
                    'warehouse_id':self._get_warehouse(),#line.order_id.picking_type_id.warehouse_id.id,
                }   
                line.compute_done = True 
                lines.append(template)
        return lines

    # @api.multi #odoo13
    def create_picking(self):
        for order in self:
            moves = self._crete_move_line()
            res = order._prepare_picking()
            if not moves:
                raise UserError(_('Moves are already created.'))
            if moves:
                picking = self.env['stock.picking'].create(res)
                for val in moves:
                    val.update({'picking_id': picking.id})
                    self.env['stock.move'].create(val)
        return True 
        
    def action_view_internal_transfer(self, cr, uid, ids, context=None):
        template_obj = self.pool.get("product.template")
        templ_ids = list(set([x.product_tmpl_id.id for x in self.browse(cr, uid, ids, context=context)]))
        return template_obj.action_view_routes(cr, uid, templ_ids, context=context)

class hr_department(models.Model):
    _inherit = 'hr.department'

    custom_location_id = fields.Many2one(
        'stock.location',
        'Department Location',
        company_dependent=True,
        domain="[('company_id', '=', current_company_id)]",
     )

class stock_picking(models.Model):
    _inherit = 'stock.picking'
    custom_equipment_request_id = fields.Many2one('maintenance.request','Equipment request id')
    
class purchase_requisition(models.Model):
    _inherit = 'purchase.requisition'
    custom_equipment_request_id = fields.Many2one('maintenance.request','Equipment request id')

class equipment_parts_line(models.Model):
    _name = 'equipment.parts.line'

    @api.onchange('product_id')
    def _product_qty(self):
        self.product_stock = self.product_id.qty_available

    product_id = fields.Many2one('product.product','Product')
    qty = fields.Float(string="Quantity")
    compute_done = fields.Boolean(string="Compute Done")
    product_stock = fields.Float(string="Product Stock")
    request_id1 = fields.Many2one('maintenance.request','PO line id')
    request_id2 = fields.Many2one('maintenance.request','Transfer id')
    request_id3 = fields.Many2one('maintenance.request','Needed Parts Id')

