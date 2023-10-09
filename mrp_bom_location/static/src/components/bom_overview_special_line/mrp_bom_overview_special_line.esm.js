/** @odoo-module **/

import {BomOverviewSpecialLine} from "@mrp/components/bom_overview_special_line/mrp_bom_overview_special_line";
import {patch} from "@web/core/utils/patch";

patch(BomOverviewSpecialLine, "mrp_bom_location", {
    props: {
        ...BomOverviewSpecialLine.props,
        showOptions: {
            ...BomOverviewSpecialLine.showOptions,
            location: Boolean,
        },
    },
});
