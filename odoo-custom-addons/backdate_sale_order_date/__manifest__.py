# -*- coding: utf-8 -*-
#Waiyaki, Simplivity Business Systems
# Copyright (C) 2022-Simplivity Business Systems <simplivity.co.ke>

{
    'name': "Backdate Sale Order Date",

    'summary': """
        Allow a user to backdate the sale order date.
        """,

    'description': """
       By default, the order date is automatically generated.
       This module allows the user to specify the sale order date. The order date is also updated on the stock delivery date
    """,
    'price': 100.00,
    'currency': 'USD',

    'author': "Simplivity Business Systems",
    'website': "http://www.simplivity.co.ke",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'sales',
    'version': '0.1',
    'license': 'OPL-1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale',],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
