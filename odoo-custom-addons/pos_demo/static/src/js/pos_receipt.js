odoo.define('pos_receipt.custom', function(require) {
    "use strict";

    //    initializing variables

    var core = require('web.core');
    var rpc = require('web.rpc');
    var screens = require('point_of_sale.screens');

    var pos_model = require('point_of_sale.models');
    pos_model.load_fields("product.product", "standard_price");

//    customizing POS receipt

    screens.ReceiptScreenWidget.include({
        get_receipt_render_env: function(){
            var receipt_env = this.super();
            var order = this.pos.get_order();
            var saved = 0;
            _.each(order.orderlines.models, function (line) {
                saved += ((line.product.list_price - line.get_base_price()) * line.quantity);
            });
            receipt_env['saved amount'] = saved;
            return receipt_env;
        }
    });

    screens.OrderWidget.include({
        set_value: function(val){
            this._super(val);
            var orderline = this.pos.get_order().get_selected_orderline();
            var standard_price = orderline.product.standard_price;
            if(orderline && standard_price) {
                var line_price = orderline.get_base_price();
                if (line_price < orderline.quantity * standard_price) {
                    this.gui.show_popup('alert', {
                    title: 'Warning',
                    body:"Product price is set below product's actual cost",
                    }
                    });
                }
            }
        }
    });

    var discount_button = screens.ActionButtonWidget.extend({
        template: 'BtnDiscount',
        button_click: function(){
        var order = this.pos.get_order();
        if (order.selected_orderline) {
        order.selected_orderline.set_discount(5);
        }
        }
    });

    screens.define_action_button({
        'name': 'discount_btn',
        'widget': discount_button
    });

    var lastOrder = screens.ActionButtonWidget.extend({
        template: 'LastOrders',
        button_click: function(){
            var self = this;
            var order = this.pos.get_order();
            if (order.attributes.client) {
                var domain = [['partner_id', '=', order.attributes.client.id]];
                rpc.query({
                model: 'pos.order',
                method: 'search_read',
                rgs: [domain, ['name', 'amount_total', 'cu']],
                kwargs: {limit:5},
                }).then(function(orders){
                    if(orders.length > 0) {
                    var order_list = _.map(orders, function(0){
                        return {'label': _str.sprintf("%s - TOTAL %s", o.name, o.amount_total)};
                    });
                    self.show_order_list(order_list);
                    } else {
                        self.show_error('No previous order found for the customer');
                    }
                });

                }
                else {
                    this.show_error('Please select the customer');
                }
            },
            show_order_list: function(list){
                this.gui.show_popup('selection', {
                    'title': 'Last 5 orders',
                    'list': list,
                    'confirm': function(reward){
                        order.apply_reward(reward);
                    },
                });
        },
        show_error:function (message) {
        this.gui.show_popup('error', {
            'title': 'Warning',
            'body': message,
        });
        }
    });

    screens.define_action_button({
        'name': 'last_order',
        'widget': lastOrders
    });
});