/** @odoo-module **/

import {BomOverviewComponent} from "@mrp/components/bom_overview/mrp_bom_overview";
import {BomOverviewDisplayFilter} from "@mrp/components/bom_overview_display_filter/mrp_bom_overview_display_filter";
import {BomOverviewLine} from "@mrp/components/bom_overview_line/mrp_bom_overview_line";
import {BomOverviewTable} from "@mrp/components/bom_overview_table/mrp_bom_overview_table";
import {patch} from "@web/core/utils/patch";
import {useService} from "@web/core/utils/hooks";

const {EventBus, onWillStart, useSubEnv, useState} = owl;

patch(BomOverviewTable.prototype, "test patch", {
    get showDomain() {
        return this.props.showOptions.domain;
    },
});

patch(BomOverviewTable.props.showOptions, "test patch 2", {
    shape: {
        ...BomOverviewTable.props.showOptions.shape,
        domain: Boolean,
    },
});

patch(BomOverviewDisplayFilter.prototype, "test patch 2", {
    setup() {
        this.displayOptions = {
            availabilities: this.env._t("Availabilities"),
            domain: this.env._t("Domain"),
            leadTimes: this.env._t("Lead Times"),
            costs: this.env._t("Costs"),
            operations: this.env._t("Operations"),
        };
    },
});

patch(BomOverviewDisplayFilter.props.showOptions, "test patch 2", {
    shape: {
        ...BomOverviewTable.props.showOptions.shape,
        domain: Boolean,
    },
});

patch(BomOverviewLine.prototype, "test patch", {
    get showDomain() {
        return this.props.showOptions.domain;
    },

    get hasDomain() {
        return Object.prototype.hasOwnProperty.call(this.data, "domain");
    },
});

patch(BomOverviewLine.props.showOptions, "test patch 2", {
    shape: {
        ...BomOverviewTable.props.showOptions.shape,
        domain: Boolean,
    },
});

patch(BomOverviewComponent.prototype, "test patch 3", {
    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");

        this.variants = [];
        this.warehouses = [];
        this.showVariants = false;
        this.uomName = "";
        this.extraColumnCount = 0;
        this.unfoldedIds = new Set();

        this.state = useState({
            showOptions: {
                uom: false,
                domain: true,
                availabilities: false,
                costs: true,
                operations: true,
                leadTimes: true,
                attachments: false,
            },
            currentWarehouse: null,
            currentVariantId: null,
            bomData: {},
            precision: 2,
            bomQuantity: null,
        });

        useSubEnv({
            overviewBus: new EventBus(),
        });

        onWillStart(async () => {
            await this.getWarehouses();
            await this.initBomData();
        });
    },
    async getBomData() {
        const args = [
            this.activeId,
            this.state.bomQuantity,
            this.state.currentVariantId,
        ];
        const context = this.state.currentWarehouse
            ? {warehouse: this.state.currentWarehouse.id}
            : {};
        const bomData = await this.orm.call(
            "mrp_bom_configurable.report.mrp.report_bom_structure",
            "get_html",
            args,
            {context}
        );
        this.state.bomData = bomData.lines;
        this.state.showOptions.attachments = bomData.has_attachments;
        return bomData;
    },
});
