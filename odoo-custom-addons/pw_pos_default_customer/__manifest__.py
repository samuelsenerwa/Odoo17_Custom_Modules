# -*- coding: utf-8 -*-
{
    'name': 'POS Default Customer',
    'version': '1.0',
    'author': 'Preway IT Solutions',
    'category': 'Point of Sale',
    'depends': ['point_of_sale'],
    'summary': 'This apps helps you set default customer on POS',
    'description': """
- Default customer on POS.
    """,
    'data': [
        'views/pos_config_view.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pw_pos_default_customer/static/src/js/**/*',
        ],
    },
    'application': True,
    'installable': True,
    "license": "LGPL-3",
    "images":["static/description/Banner.png"],
}
