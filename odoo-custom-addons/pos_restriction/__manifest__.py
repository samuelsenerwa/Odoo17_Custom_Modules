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
    'category': 'Point of Sale',
    'depends': ['base', 'point_of_sale', 'stock'],
    'data': [
        'views/pos_config_view.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_restriction/static/src/app/models/models.js',
        ],
    },
    'demo': [
        'demo/demo.xml',
    ],
    'application': False,
    'installable': True,
    'license': 'LGPL-3',
}
