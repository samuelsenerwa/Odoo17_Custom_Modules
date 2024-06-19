odoo.define('pos_stock_warning.pos', function(require) {
	"use strict";
    console.log("pos_stock_warning.pos loaded");

	const models = require('point_of_sale.models');

	models.load_fields('res.company', ['point_of_sale_update_stock_quantities'])

	models.load_fields('product.product', ['type','virtual_available',
		'available_quantity','qty_available','incoming_qty','outgoing_qty']);
	models.load_fields('pos.config', ['stock_location_id'])

	models.load_models({
		model: 'stock.location',
		fields: [],
		domain: function(self){
            var domain = [['company_id','=',false]];
            if (self.company) domain.push(['company_id', '=', self.company.id]);
            return domain;
        },
		loaded: function(self, locations){
			self.locations = locations[0];
			if (self.config.show_stock_location == 'specific')
			{
				self.locations =  self.config.stock_location_id[0];
			}
		},
	});

});