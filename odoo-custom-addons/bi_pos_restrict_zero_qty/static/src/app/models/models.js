/** @odoo-module */

import { Order, Orderline, Payment } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { markRaw, reactive } from "@odoo/owl";

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
           var config_id=self.env.services.pos.config.id;
           let prod_used_qty = {};
           let restrict = false;
           if(pos_config.restrict_zero_qty){
               $.each(lines, function( i, line ){
                   let prd = line.product;
                   if (prd.type == 'product'){
                       if(prd.id in prod_used_qty){
                           let old_qty = prod_used_qty[prd.id][1];
                           prod_used_qty[prd.id] = [prd.qty_available,line.quantity+old_qty]
                       }else{
                           prod_used_qty[prd.id] = [prd.qty_available,line.quantity]
                       }
                   }
                   if (prd.type == 'product'){
                       if(prd.qty_available <= 0){
                           restrict = true;
                           call_super = false;
                           let warning = prd.display_name + ' is out of stock.';
                           this.env.services.pos.popup.add(ErrorPopup, {
                               title: _t('Zero Quantity Not allowed'),
                               body: _t(warning),
                           });
                       }
                   }
               });
                   if(restrict === false){
                       $.each(prod_used_qty, function( i, pq ){
                           let product = self.env.services.pos.db.get_product_by_id(i);
                           let check = pq[0] - pq[1];
                           let warning = product.display_name + ' is out of stock.';
                           if (product.type == 'product'){
                               if (check < 0){
                                   call_super = false;
                                   this.env.services.pos.popup.add(ErrorPopup, {
                                       title: _t('Deny Order'),
                                       body: _t(warning),
                                   });
                               }
                           }
                       });
                   }
           }
           if(call_super){
               super.pay();
           }
    },

});