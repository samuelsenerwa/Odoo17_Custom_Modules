# -*- coding: utf-8 -*-
{
    'name': "pos_show_product_quantity",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales/Point of Sale',
    'version': '17.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['point_of_sale'],

    "assets": {
        "point_of_sale._assets_pos":[
            "pos_show_product_quantity/static/src/**/**",
        ],
    },

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    "application": False,
    "installable": True,
    "auto_install": False,
    "license": "Other proprietary",
}

