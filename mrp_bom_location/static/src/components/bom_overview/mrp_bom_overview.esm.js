/** @odoo-module **/

import {BomOverviewComponent} from "@mrp/components/bom_overview/mrp_bom_overview";
import {patch} from "@web/core/utils/patch";

patch(BomOverviewComponent.prototype, "mrp_bom_location", {
    setup() {
        this._super.apply();
        this.state.showOptions.location = true;
    },

    getReportName() {
        return (
            this._super.apply(this, arguments) +
            "&show_location=" +
            this.state.showOptions.location
        );
    },
});
