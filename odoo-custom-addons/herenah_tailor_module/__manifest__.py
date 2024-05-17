# -*- coding: utf-8 -*-
{
    'name': "Herenah Tailoring Module",

    'summary': "Enables effective management of the tailors and packers",
    'sequence': -100,
    'description': """
This modules enables herenah fashion designers to easily manage the tailors and packers assigned the orders
    """,

    'author': "Linkyou Systems ",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mrp'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/mrp_production.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
'application': True,
}

