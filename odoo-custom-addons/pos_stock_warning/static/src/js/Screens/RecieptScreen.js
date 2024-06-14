odoo.define('pos_stock_warning.ReceiptScreen', function(require) {
	"use strict";

	const Registries = require('point_of_sale.Registries');
	const ReceiptScreen = require('point_of_sale.ReceiptScreen');

	const BiReceiptScreen = (ReceiptScreen) =>
		class extends ReceiptScreen {
			constructor() {
				super(...arguments);
				let self = this;
				const order = this.currentOrder;
				let config = this.env.pos.config;
				let stock_update = this.env.pos.company.point_of_sale_update_stock_quantities;
				if (config.pos_display_stock === true && stock_update == 'real' &&
					(config.pos_stock_type == 'onhand' || config.pos_stock_type == 'available'))
				{
					order.get_orderlines().forEach(function (line) {
						var product = line.product;
						product['bi_on_hand'] -= line.get_quantity();
						product['bi_available'] -= line.get_quantity();
						product.qty_available -= line.get_quantity();
						product.virtual_available -= line.get_quantity();

						self.load_product_qty(product);
					})
				}
				this.env.pos.set("is_sync",true);
			}

			load_product_qty(product){
				let product_qty_final = $("[data-product-id='"+product.id+"'] #stockqty");
				product_qty_final.html(product['bi_on_hand'])

				let product_qty_avail = $("[data-product-id='"+product.id+"'] #availqty");
				product_qty_avail.html(product['bi_available']);
			}
		};

	Registries.Component.extend(ReceiptScreen, BiReceiptScreen);

	return ReceiptScreen;

});