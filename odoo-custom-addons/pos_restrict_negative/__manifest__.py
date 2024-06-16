# -*- coding: utf-8 -*-
{
    'name': "pos_restrict_negative",
    'version': "17.0.1.1",
    "category": "Point of Sale",
    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
        The point of sale module restricts selling in a given POS session if you've got Zero quantities
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list

    # any module necessary for this one to work correctly
    'depends': ['base', 'point_of_sale', 'stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/pos_config_view.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_restrict_negative/static/src/app/models/models.js',
        ],
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    "application": False,
    "installable": True,
}
