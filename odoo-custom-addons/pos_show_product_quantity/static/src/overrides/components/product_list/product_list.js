/** @odoo-module */

import {patch} from "@web/core/utils/patch";
import {ProductsWidget} from "@point_of_sale/app/screens/product_screen/product_list/product_list";

patch(ProductsWidget.prototype, {
    get productsToDisplay() {
        var self = this;
        var result = super.productToDisplay;

        if(self.env.service.pos.config.hide_out_of_stock) {
            var available_product = [];

            $.each(result, function(index, product) {
                if(product.qty_available > 0 || product.type == "service") {
                    available_product.push(product);
                }
            });
            result = available_product;
        }
        return result;
    },
})