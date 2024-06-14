odoo.define('pos_stock_warning.ProductsWidget', function(require) {
	"use strict";

	const Registries = require('point_of_sale.Registries');
	// const PosComponent = require('point_of_sale.PosComponent');
	const ProductsWidget = require('point_of_sale.ProductsWidget');

	let prd_list_count = 0;

	const BiProductsWidget = (ProductsWidget) =>
		class BiProductsWidget extends ProductsWidget {
			constructor() {
				super(...arguments);
			}

			mounted() {
				super.mounted();
				this.env.pos.on('change:is_sync', this.render, this);
			}
			willUnmount() {
				super.willUnmount();
				this.env.pos.off('change:is_sync', null, this);
			}

			_switchCategory(event) {
				this.env.pos.set("is_sync",true);
				super._switchCategory(event);
			}

			get is_sync() {
				return this.env.pos.get('is_sync');
			}
			get productsToDisplay() {
				let self = this;
				let prods = super.productsToDisplay;

				if (self.env.pos.config.show_stock_location == 'specific')
				{
					let prod_ids = [];
					$.each(prods, function( i, prd ){
						prod_ids.push(prd.id)
					});
					let x_sync = self.env.pos.get("is_sync");
					let location = self.env.pos.config.stock_location_id;
					if(x_sync == true || !("bi_on_hand" in prods) || !("bi_available" in prods)){
						if (self.env.pos.config.pos_stock_type == 'onhand'){
							this.rpc({
								model: 'stock.quant',
								method: 'get_products_stock_location_qty',
								args: [1, location[0],prod_ids],
							}).then(function(output) {
								self.env.pos.loc_onhand = output[0];
								$.each(prods, function( i, prd ){
									prd['bi_on_hand'] = prd.qty_available;
									prd['bi_available'] = prd.virtual_available;
									for(let key in self.env.pos.loc_onhand){
										if(prd.id == key){
											prd['bi_on_hand'] = self.env.pos.loc_onhand[key];
											prd['updated_price'] = self.env.pos.loc_onhand[key];
										}
									}
								});
								self.env.pos.set("is_sync",false);
							});
						}
						if (self.env.pos.config.pos_stock_type == 'available')
						{
							this.rpc({
								model: 'product.product',
								method: 'get_stock_location_avail_qty',
								args: [1, location[0],prod_ids],
							}).then(function(output) {
								self.env.pos.loc_available = output[0];

								$.each(prods, function( i, prd ){
									prd['bi_on_hand'] = prd.qty_available;
									prd['bi_available'] = prd.virtual_available;
									for(let key in self.env.pos.loc_available){
										if(prd.id == key)
										{
											prd['bi_available'] = self.env.pos.loc_available[key];
											prd['updated_virtual'] = self.env.pos.loc_available[key];
										}
									}
								});
								self.env.pos.set("is_sync",false);
							});
						}
					}else{
						$.each(prods, function( i, prd ){
							if(prd.bi_on_hand != prd.updated_price){
								prd['bi_on_hand'] = prd.qty_available;
							}
							if(prd.bi_available != prd.updated_virtual){
								prd['bi_available'] = prd.virtual_available;
							}
						});
					}
				}
				else{
					$.each(prods, function( i, prd ){
						prd['bi_on_hand'] = prd.qty_available;
						prd['bi_available'] = prd.virtual_available;
					});
				}
				return prods
			}
		};

	Registries.Component.extend(ProductsWidget, BiProductsWidget);

	return ProductsWidget;

});