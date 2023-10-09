/** @odoo-module **/

import {registry} from "@web/core/registry";

const {Component} = owl;

export class InputLineSelect extends Component {}

InputLineSelect.template = "input_line.select";
InputLineSelect.props = ["value", "possibleVal"];
