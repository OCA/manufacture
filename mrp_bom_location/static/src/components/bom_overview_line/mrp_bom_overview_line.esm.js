/** @odoo-module **/

import {BomOverviewLine} from "@mrp/components/bom_overview_line/mrp_bom_overview_line";
import {patch} from "@web/core/utils/patch";

patch(BomOverviewLine.prototype, "mrp_bom_location", {
    // ---- Handlers ----

    async goToLocation() {
        return this.actionService.doAction({
            name: this.env._t("Locations"),
            type: "ir.actions.act_window",
            res_model: "stock.location",
            domain: [["complete_name", "=", this.data.location]],
            views: [
                [false, "tree"],
                [false, "form"],
            ],
            target: "current",
        });
    },
});

patch(BomOverviewLine, "mrp_bom_location", {
    props: {
        ...BomOverviewLine.props,
        showOptions: {
            ...BomOverviewLine.showOptions,
            location: Boolean,
        },
    },
});
