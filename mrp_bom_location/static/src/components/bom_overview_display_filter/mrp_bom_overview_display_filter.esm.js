/** @odoo-module **/

import {BomOverviewDisplayFilter} from "@mrp/components/bom_overview_display_filter/mrp_bom_overview_display_filter";
import {patch} from "@web/core/utils/patch";

patch(BomOverviewDisplayFilter.prototype, "mrp_bom_location", {
    setup() {
        this._super.apply();
        this.displayOptions.location = this.env._t("Location");
    },
});

patch(BomOverviewDisplayFilter, "mrp_bom_location", {
    props: {
        ...BomOverviewDisplayFilter.props,
        showOptions: {
            ...BomOverviewDisplayFilter.showOptions,
            location: Boolean,
        },
    },
});
