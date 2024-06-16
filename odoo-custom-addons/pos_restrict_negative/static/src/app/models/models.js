/** @odoo-module */

import { Order, Orderline, Payment } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { _t } from "@web/core/l10n/translation";

patch(Order.prototype, {
    setup() {
        super.setup(...arguments);
    },
    async pay() {
        var self = this;
        let order = this.env.services.pos.get_order();
        let lines = order.get_orderlines();
        let pos_config = self.env.services.pos.config;
        let call_super = true;
        let restrict = false;
        let stock_location_id = pos_config.stock_location_id.id;

        if (pos_config.restrict_zero_qty) {
            $.each(lines, function (i, line) {
                let prd = line.product;
                if (prd.type == 'product') {
                    let qty_available_in_location = (prd.quantities_by_location && prd.quantities_by_location[stock_location_id]) || 0;
                    if (qty_available_in_location <= 0 || line.quantity <= 0) {
                        restrict = true;
                        call_super = false;
                        let warning = prd.display_name + ' is out of stock in the current location or quantity is zero/negative.';
                        self.env.services.pos.popup.add(ErrorPopup, {
                            title: _t('Zero Quantity Not allowed'),
                            body: _t(warning),
                        });
                    }
                }
            });
        }
        if (call_super) {
            super.pay();
        }
    },
});



//
//import { Order, Orderline, Payment } from "@point_of_sale/app/store/models";
//import { patch } from "@web/core/utils/patch";
//import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
//import { _t } from "@web/core/l10n/translation";
//
//patch(Order.prototype, {
//    setup() {
//        super.setup(...arguments);
//    },
//    async pay() {
//        var self = this;
//        let order = this.env.services.pos.get_order();
//        let lines = order.get_orderlines();
//        let pos_config = self.env.services.pos.config;
//        let call_super = true;
//        var config_id = self.env.services.pos.config.id;
//        let prod_used_qty = {};
//        let restrict = false;
//        let stock_location_id = pos_config.stock_location_id.id;
//
//        if (pos_config.restrict_zero_qty) {
//            $.each(lines, function (i, line) {
//                let prd = line.product;
//                if (prd.type == 'product') {
//                    if (prd.id in prod_used_qty) {
//                        let old_qty = prod_used_qty[prd.id][1];
//                        prod_used_qty[prd.id] = [prd.qty_available, line.quantity + old_qty];
//                    } else {
//                        prod_used_qty[prd.id] = [prd.qty_available, line.quantity];
//                    }
//                }
//                if (prd.type == 'product') {
//                    let qty_available_in_location = prd.quantities_by_location[stock_location_id] || 0;
//                    if (qty_available_in_location <= 0) {
//                        restrict = true;
//                        call_super = false;
//                        let warning = prd.display_name + ' is out of stock in the current location.';
//                        this.env.services.pos.popup.add(ErrorPopup, {
//                            title: _t('Zero Quantity Not allowed'),
//                            body: _t(warning),
//                        });
//                    }
//                }
//            });
//            if (restrict === false) {
//                $.each(prod_used_qty, function (i, pq) {
//                    let product = self.env.services.pos.db.get_product_by_id(i);
//                    let qty_available_in_location = product.quantities_by_location[stock_location_id] || 0;
//                    let check = qty_available_in_location - pq[1];
//                    let warning = product.display_name + ' is out of stock in the current location.';
//                    if (product.type == 'product') {
//                        if (check < 0) {
//                            call_super = false;
//                            this.env.services.pos.popup.add(ErrorPopup, {
//                                title: _t('Deny Order'),
//                                body: _t(warning),
//                            });
//                        }
//                    }
//                });
//            }
//        }
//        if (call_super) {
//            super.pay();
//        }
//    },
//});
