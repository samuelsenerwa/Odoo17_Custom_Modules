# -*- coding: utf-8 -*-
{
    "name": "POS Stock Display",
    "version": "17.0.1.0.0",
    "category": "Point of Sale",
    "depends": ["base", "sale_management", "stock", "point_of_sale"],
    "description": "Display stock levels in the POS interface.",
    "data": [
        "views/custom_pos_config_view.xml",
    ],
    "assets": {
        "point_of_sale.assets": [
            "pos_stock_warning/static/src/js/Chrome.js",
            "pos_stock_warning/static/src/js/models.js",
            "pos_stock_warning/static/src/js/SyncStock.js",
            "pos_stock_warning/static/src/js/Screens/ProductScreen.js",
            "pos_stock_warning/static/src/js/Screens/ProductsWidget.js",
            "pos_stock_warning/static/src/js/Screens/ReceiptScreen.js",
        ],
        "web.assets_qweb": [
            "pos_stock_warning/static/src/xml/**/*",
        ],
    },
    "auto_install": False,
    "installable": True,
    "license": "AGPL-3",
}