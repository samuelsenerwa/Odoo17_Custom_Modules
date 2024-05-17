# -*- coding: utf-8 -*-
{
    'name': "Herenah Salary Advance",

    'summary': "This modules manages the salary advance paid to workers, it works hand in hand with payroll module",
    "sequence": -100,
    'description': """
        The basic functionality of this module is that it handles all salary advance payments made to all the employees working for herenah fashion designers for effective accounting process
""",
    'author': "Linkyou Systems",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['om_hr_payroll'],

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
    'application': True,
}
