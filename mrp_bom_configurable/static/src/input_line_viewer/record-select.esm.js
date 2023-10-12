/** @odoo-module **/

import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";
import {debounce} from "@web/core/utils/timing";

const {Component, useState, onMounted, useRef, onWillUpdateProps, onRendered} = owl;

class RecordItem extends Component {
    setup() {
        this.ref = useRef("item");

        onMounted(() => {
            this.ref.el.addEventListener("click", (event) => {
                this.props.click(event, this.props.id);
            });
        });
    }
}

RecordItem.template = "input_line.record_item";
RecordItem.props = ["click", "name", "id"];

export class RecordSelect extends Component {
    state = useState({
        open: false,
        loading: false,
        possibleValues: [],
        filteredValues: [],
        selectedValue: {},
    });

    setup() {
        this.baseInput = useRef("baseInput");
        this.orm = useService("orm");
        this.searchPossibleValues = debounce(this.searchPossibleValues, 200);
        this.state.selectedValue = this.props.value;

        onWillUpdateProps((nextProps) => {
            if (nextProps.value != this.props.value) {
                this.state.selectedValue.display_name = nextProps.value.display_name;
                this.state.selectedValue.id = nextProps.value.value;
            }
        });

        onMounted(() => {
            this.baseInput.el.addEventListener("click", async (event) => {
                event.stopPropagation();
                if (!this.state.open) {
                    this.state.open = true;
                    this.state.loading = true;
                    this.state.filteredValues = [];

                    this.state.possibleValues = await this.searchPossibleValues();
                    this.state.loading = false;
                    this.state.filteredValues = this.state.possibleValues;
                }
            });

            this.baseInput.el.addEventListener("keydown", (ev) => {
                if (ev.key === "Escape") {
                    this.state.open = false;
                    ev.target.blur();
                    return;
                }
            });

            this.baseInput.el.addEventListener("input", async (ev) => {
                const searchTerms = ev.target.value;

                this.state.filteredValues = this.state.possibleValues.filter(
                    (item) =>
                        searchTerms == "" || item.display_name.includes(searchTerms)
                );
            });

            document.addEventListener("click", (ev) => {
                this.state.open = false;
            });
        });
    }

    // Methods passed as prop must be bound to this in the xml
    // so that this refers to the proper instance
    clickItem(event, id) {
        event.stopPropagation();
        const value = this.state.filteredValues.find((item) => item.id === id);
        // We need selectedValue to act as a buffer between the change of
        // value and the saving
        // on save we can change the props and the state will be updated on
        // onWillUpdateProps
        this.props.value.value = value.id;
        this.props.value.display_name = value.display_name;
        this.state.open = false;
        this.props.notifyChange();
    }

    searchPossibleValues() {
        return new Promise(async (res, rej) => {
            const ids = await this.orm.search(this.props.model, this.props.domain);
            const values = await this.orm.read(this.props.model, ids, [
                "id",
                "display_name",
            ]);
            res(values);
        });
    }
}

RecordSelect.components = {RecordItem};
RecordSelect.template = "input_line.record_select";
RecordSelect.props = ["model", "value", "domain", "notifyChange"];
