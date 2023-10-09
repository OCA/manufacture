/** @odoo-module **/

import {BomOverviewTable} from "@mrp/components/bom_overview_table/mrp_bom_overview_table";
import {patch} from "@web/core/utils/patch";

patch(BomOverviewTable.prototype, "mrp_bom_location", {
    // ---- Getters ----

    get showLocation() {
        return this.props.showOptions.location;
    },
});

patch(BomOverviewTable, "mrp_bom_location", {
    props: {
        ...BomOverviewTable.props,
        showOptions: {
            ...BomOverviewTable.showOptions,
            location: Boolean,
        },
    },
});
