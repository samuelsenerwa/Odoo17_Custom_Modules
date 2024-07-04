/** @odoo-module */

import {patch} from "@web/core/utils/patch";
import {PosStore} from "@point_of_sale/app/store/pos_store";

patch(PosStore.prototype, {
        _loaderProductProduct(product) {
        var self = this;
        super._loaderProductProduct(...arguments);

        for (const prod of products) {
            self.db.product_by_id[prod.id].pos_qty_available = prod.pos_qty_available
            }
        },
});