/** @odoo-module */

import {patch} from "@web/core/utils/patch";
import {ProductCard} from "@point_of_sale/app/generic_components/product_card/product_card";

patch(ProductCard, {
    props: {
        ...ProductCard.props,
        qty: Number,
    },
});