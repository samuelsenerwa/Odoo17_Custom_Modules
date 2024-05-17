/** @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";


patch(Order.prototype, {
    setup() {
        super.setup(...arguments);
        if (this.pos.config.pos_customer_id) {
            var default_customer = this.pos.config.pos_customer_id[0];
            var partner = this.pos.db.get_partner_by_id(default_customer);
            this.set_partner(partner);
        }
    },
});
