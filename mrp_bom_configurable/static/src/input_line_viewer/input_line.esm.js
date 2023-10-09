/** @odoo-module **/

import {registry} from "@web/core/registry";
import {getDefaultConfig} from "@web/views/view";
import {Layout} from "@web/search/layout";
import {Notebook} from "@web/core/notebook/notebook";
import {useService} from "@web/core/utils/hooks";
import {x2ManyCommands} from "@web/core/orm_service";

import {InputLineSelect} from "./select.esm";
import {RecordSelect} from "./record-select.esm";

const {Component, useSubEnv, useState, onWillStart, useRef, onMounted} = owl;

class InputLine extends Component {
    state = useState({
        bomData: {data: []},
        inputLineData: [],
        dataChanged: false,
        alert: undefined,
        message: undefined,
    });

    setup() {
        useSubEnv({
            config: {
                ...getDefaultConfig(),
                ...this.env.config,
            },
        });
        this.display = {
            controlPanel: {"top-right": false, "bottom-right": false},
        };
        this.orm = useService("orm");

        onWillStart(async () => {
            await this.getInputLineData();
            const check = await this.orm.call(
                "input.line",
                "check_one_data",
                [this.activeId]
            );
            this.state.alert = check[0];
            this.state.message = check[1];
        });

        this.form = useRef("inputLineForm");
        this.state.dataChanged = false;
        onMounted(() => {
            this.form.el.addEventListener("change", () => {
                this.setDataChanged();
            });
        });
    }

    async getInputLineData() {
        this.state.bomData = await this.orm.call("input.line", "get_json", [
            this.activeId,
        ]);
        this.state.inputLineData = await this.orm.call(
            "input.line",
            "get_values_with_field_desc",
            [this.activeId]
        );
    }

    async setDataChanged() {
        this.state.dataChanged = true;
    }

    get activeId() {
        return this.props.action.context.active_id;
    }

    async save() {
        this.saving = true;
        
        const data = {};
        this.state.inputLineData.forEach((element) => {
            if (element.type == "many2one") {
                data[element.name] = element.value;
            }
            else {
                data[element.name] = element.value;
            }
        });

        await this.orm.write(
            "input.line",
            [this.activeId],
            data,
        );
        await this.orm.call(
            "input.line",
            "ui_configure",
            [this.activeId]
        );

        await this.getInputLineData();

        const check = await this.orm.call(
            "input.line",
            "check_one_data",
            [this.activeId]
        );
        this.state.alert = check[0];
        this.state.message = check[1];

        this.saving = false;
    }

    async cancel() {
        this.state.bomData = await this.orm.call("input.line", "get_json", [
            this.activeId,
        ]);
        this.state.inputLineData = await this.orm.call(
            "input.line",
            "get_values_with_field_desc",
            [this.activeId]
        );
        this.state.dataChanged = false;
    }
}

InputLine.components = {Layout, Notebook, InputLineSelect, RecordSelect};
InputLine.template = "input_line.clientaction";

registry.category("lazy_components").add("InputLine", InputLine);
