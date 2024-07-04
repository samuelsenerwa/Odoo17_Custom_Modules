odoo.define('pos_demo.custom', function (require) {
    "use strict";

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');
    const pos_model = require('point_of_sale.models');

//    modifying the point of sale screen UI
    pos_model.load_fields("product.product", ["standard_price"]);

    class PosDiscountButton extends PosComponent {
        async onClick() {
        const order = this.env.pos.get_order();
        if(order.selected_orderline) {
             order.selected_orderline.set_discount(5);
            }
        }
    }
    PosDiscountButton.template = 'PosDiscountButton';
    PosProductScreen.addControlButton({
        component: PosDiscountButton,
        condition: function() {
            return this.env.pos.config.module_pos_discount;
        },
    });
    Registries.Component.add(PosDiscountButton);

//    Making RPC call
    class PosLastOrderButton extends PosComponent {
        async onClick() {
            var self = this;
            const order = this.env.pos.get_order();
            if (order.attributes.client) {
                var domain = [['partner_id', '=', order.attributes.client.id]];
                this.rpc({
                    model: 'pos.order',
                    method:'search_read',
                    args:[domain, ['name', 'amount_total']],
                    kwargs: {limit:5},
                }).then(function(orders){
                    if(orders.length > 0) {
                    var order_list = _.str.sprint("%s - TOTAL: %s", o.name, o.amount_total)
                    };
                });
            } else {
                self,.showPopup('ErrorPopup', {
                    title: self.env._t('Error'),
                    body: self.env._t("Please select a customer."),
                });
            }
        }
    }
    PosLastOrderButton.template = 'PosLastOrderButton';
    ProductScreen.addControlButton({
        component: PosLastOrderButton,
        condition: function() {
        return true;
//            return this.env.pos.config.module_pos_last_order;
        },
    });
    Registries.Component.add(PosLastOrderButton);

//    changing business logic
    const UpdatedProductScreen = ProductScreen =>
        class extends ProductScreen {
            _setValue(val) {
                super._setValue(val);
                const orderline = this.env.pos.get_order().selected_orderline;
                if (orderline && orderline.product.standard_price) {
                    var price_unit = orderline.get_unit_price() * (1.0 - (orderline.get_discount() / 100.0));
                    if(orderline.product.standard_price > price_unit) {
                        this.showPopup('ErrorPopup', {title: 'Warning', 'body': 'Product price set below cost of product.'})
                    }
                }
            }
        };
    Registries.Component.extend(ProductScreen, updateProductScreen);
    return PosDiscountButton;
});