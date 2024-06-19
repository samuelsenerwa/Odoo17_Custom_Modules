odoo.define('pos_stock_warning.productScreen', function(require) {
	"use strict";

	const Registries = require('point_of_sale.Registries');
	const ProductScreen = require('point_of_sale.ProductScreen');

	const BiProductScreen = (ProductScreen) =>
		class extends ProductScreen {
			constructor() {
				super(...arguments);
			}
			async _clickProduct(event) {
				let self = this;
				const product = event.detail;
				console.log("Product clicked:", product);
				let allow_order = self.env.pos.config.pos_allow_order;
				let deny_order= self.env.pos.config.pos_deny_order;
				let call_super = true;
				if(self.env.pos.config.pos_display_stock)
				{
					if(self.env.pos.config.show_stock_location == 'specific' && product.type == 'product')
					{
						var partner_id = self.env.pos.get_client();
						debugger;
						var location = self.env.pos.config.stock_location_id;
						 console.log("Making RPC call to get_single_product");
						await this.rpc({
							model: 'stock.quant',
							method: 'get_single_product',
							args: [partner_id ? partner_id.id : 0,product.id, location[0]],
						}).then(function(output) {
						console.log("RPC output:", output);
							if (allow_order == false)
							{
								if ( (output[0][1] <= deny_order) || (output[0][1] <= 0) )
								{
									call_super = false;
									self.showPopup('ErrorPopup', {
										title: self.env._t('Deny Order'),
										body: self.env._t("Deny Order" + "(" + product.display_name + ")" + " is Out of Stock."),
									});
								}
							}
							else if(allow_order == true)
							{
								if (output[0][1] <= deny_order)
								{
									call_super = false;
									self.showPopup('ErrorPopup', {
										title: self.env._t('Deny Order'),
										body: self.env._t("Deny Order" + "(" + product.display_name + ")" + " is Out of Stock."),
									});
								}
							}
						});
					}
					else{
						if (product.type == 'product' && allow_order == false)
						{
							if (product.qty_available <= deny_order && allow_order == false)
							{
								call_super = false;
								self.showPopup('ErrorPopup', {
									title: self.env._t('Deny Order'),
									body: self.env._t("Deny Order" + "(" + product.display_name + ")" + " is Out of Stock."),
								});
							}
							else if (product.qty_available <= 0 && allow_order == false)
							{
								call_super = false;
								self.showPopup('ErrorPopup', {
									title: self.env._t('Error: Out of Stock'),
									body: self.env._t("(" + product.display_name + ")" + " is Out of Stock."),
								});
							}
						}
						else if(product.type == 'product' && allow_order == true && product.qty_available <= deny_order){
							call_super = false;
							self.showPopup('ErrorPopup', {
								title: self.env._t('Error: Out of Stock'),
								body: self.env._t("(" + product.display_name + ")" + " is Out of Stock."),
							});
						}
					}
				}
				if(call_super){
					super._clickProduct(event);
				}
			}

			async _onClickPay() {
				var self = this;
				let order = this.env.pos.get_order();
				let lines = order.get_orderlines();
				let pos_config = self.env.pos.config;
				let allow_order = pos_config.pos_allow_order;
				let deny_order= pos_config.pos_deny_order;
				let call_super = true;
				if(pos_config.pos_display_stock)
				{
					if (pos_config.show_stock_location == 'specific')
					{
						let partner_id = self.env.pos.get_client();
						let location = self.env.pos.config.stock_location_id;
						let prods = [];

						$.each(lines, function( i, line ){
							if (line.product.type == 'product'){
								prods.push(line.product.id)
							}
						});
						  console.log("Making RPC call to get_products_stock_location_qty");
						await this.rpc({
							model: 'stock.quant',
							method: 'get_products_stock_location_qty',
							args: [partner_id ? partner_id.id : 0, location[0],prods],
						}).then(function(output) {
						console.log("RPC output:", output);
							var flag = 0;
							for (var i = 0; i < lines.length; i++) {
								for (var j = 0; j < output.length; j++) {
									var values = $.map(output[0], function(value, key) {
										var keys = $.map(output[0], function(value, key) {
											if (lines[i].product.type == 'product' && lines[i].product['id'] == key ){
												if (allow_order == false && lines[i].quantity > value){
													flag = flag + 1;
												}
												var check = value - lines[i].quantity;
												if (allow_order == true && deny_order > check){
													flag = flag + 1;
												}
											}
										});
									});
								}
							}
							if(flag > 0){
								call_super = false;
								self.showPopup('ErrorPopup', {
									title: self.env._t('Denied Order'),
									body: self.env._t('Ordered qty of One or more product(s) is more than available qty.'),
								});
							}
						});
					} else {
						$.each(lines, function( i, line ){
							if (line.product.type == 'product'){
								if (allow_order == false && line.quantity > line.product['bi_on_hand']){
									call_super = false;
									self.showPopup('ErrorPopup', {
										title: self.env._t('Denied Order'),
										body: self.env._t('Ordered qty of One or more product(s) is more than available qty.'),
									});
									return
								}
								var check = line.product['bi_on_hand'] - line.quantity;
								if(allow_order == true && check < deny_order){
									call_super = false;
									self.showPopup('ErrorPopup', {
										title: self.env._t('Denied Order'),
										body: self.env._t('Ordered qty of One or more product(s) is more than available qty.'),
									});
									return
								}
							}
						});
					}
				}
				if(call_super){
					super._onClickPay();
				}
			}
		};

	Registries.Component.extend(ProductScreen, BiProductScreen);

	return ProductScreen;

});