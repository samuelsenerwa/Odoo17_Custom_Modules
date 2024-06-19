# -*- coding: utf-8 -*-
{
    'name': "POS Stock Restriction",
    'summary': 'Restricts selling out of stock product quantities in the POS',
    'version': '17.0.1.1',
    'description': """
 This module adds a restriction to prevent selling products that are out of stock in the POS.
        - Adds a checkbox to the POS interface to enable/disable the restriction.
        - Allows selection of warehouse location for the POS session.
        - Shows a warning when attempting to sell out of stock products.
    """,

    'author': "Samuel Senerwa",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Point of Sale',


    # any module necessary for this one to work correctly
    'depends': ['base', 'point_of_sale', 'stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/pos_config_view.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_stock_restriction/static/src/js/models.js',
        ],
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': False,
    'installable': True,
    'license': 'LGPL-3',
}
