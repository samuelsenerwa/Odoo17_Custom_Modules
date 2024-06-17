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