/** @odoo-module **/

import {registry} from "@web/core/registry";
import {getDefaultConfig} from "@web/views/view";
import {Layout} from "@web/search/layout";
import {Notebook} from "@web/core/notebook/notebook";
import {useService} from "@web/core/utils/hooks";

import {InputLineSelect} from "./select";
import {RecordSelect} from "./record-select";

const {Component, useSubEnv, useState, onWillStart, useRef, onMounted} = owl;

class InputLine extends Component {
    state = useState({
        bomData: {data: []},
        inputLineData: [],
        dataChanged: false,
    });

    setup() {
        useSubEnv({
            config: {
                ...getDefaultConfig(),
                ...this.env.config,
            },
        });
        this.display = {
            controlPanel: { "top-right": false, "bottom-right": false },
        };
        this.orm = useService("orm");

        onWillStart(async () => {
            await this.getInputLineData();
        });

        this.form = useRef("inputLineForm");
        this.state.dataChanged = false;
        onMounted(() => {
            this.form.el.addEventListener("change", () => {
                this.state.dataChanged = true;
            });
        });
    }

    async getInputLineData() {
        this.state.bomData = await this.orm.call(
            "input.line",
            "get_json",
            [this.activeId]
        );
        this.state.inputLineData = await this.orm.call(
            "input.line",
            "get_values_with_field_desc",
            [this.activeId]
        );
    }

    setDataChanged() {
        this.state.dataChanged = true;
    }

    get activeId() {
        return this.props.action.context.active_id;
    }

    async save() {
    }

    async cancel() {
        this.state.bomData = await this.orm.call(
            "input.line",
            "get_json",
            [this.activeId]
        );
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
