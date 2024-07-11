# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'Equipment Maintenance with Purchase and Stock Management',
    'license': 'Other proprietary',
    'category': 'Inventory Management',
    'summary': 'Allow you to manage Maintenance request using Purchase and Stock',
    'price': 49.0,
    'currency': 'EUR',
    'images': ['static/description/img.jpg'],
    # 'live_test_url': 'https://youtu.be/xTmIEi0TwLg',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/hr_equipment_stock/239',#'https://youtu.be/uFfTZzhkCV8',
    'author' : 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'www.probuse.com',
    'version': '6.1.1',
    'description': """
Equipment Maintanance/Repair - Stock Management
Module is build on standard Odoo module hr_equipment. We have added stock feature in this module. 
This module allow company to track employee equipment Maintanance/Repair procedure handle by Maintainer Location. Maintainer Manager can add list of products which are going to use in Maintanance/Repair request.
Internal Transfer will create if Products are available in Company Stock/Warehouse else it will create Purchase Requisition. Based on product stock availiblity it work.
Maintainer Responsible can use to check its own Stock location and can updates in Internal transfer if needed. This is needed for example if maintainance location already have some items so no need to ask to warehouse.
maintenance request
employee maintenance request
maintenance stock
stock maintenance
Equipment Stock Management
employee stock
employee assets
employee Equipments
employee Equipment stock
stock hr
hr stock
Equipment Maintanance
Repair Stock Management
Module is build on standard Odoo module hr_equipment. We have added stock feature in this module. 

This module allow company to track employee equipment Maintanance/Repair procedure handle by Maintainer Location. Maintainer Manager can add list of products which are going to use in Maintanance/Repair request.

Internal Transfer will create if Products are available in Company Stock/Warehouse else it will create Purchase Requisition. Based on product stock availiblity it work.

Maintainer Responsible can use to check its own Stock location and can updates in Internal transfer if needed. This is needed for example if maintainance location already have some items so no need to ask to warehouse.

Employee Equipment Assign (Odoo Standard Feature)
Equipment Maintanance Request (Odoo Standard Feature)<

Stock Locations Of Maintanance and Department On Equipment Maintanance

Maintenance Lines On Maintanance Request

Related Purchase Requisition Line and Internal Transfer Line (Queue)


Integrated With Stock Operations
Links - Purchase Requisition and Internal Transfers
Purchase Requisition
material Requisition

""",
    'depends': ['stock','purchase_requisition', 'hr_maintenance'],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_equipment_data.xml',
        'views/hr_equipment_stock.xml',
    ],
    'installable': True,
    'auto_install': False,
}
