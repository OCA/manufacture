/** @odoo-module **/

const {Component} = owl;

export class InputLineSelect extends Component {}

InputLineSelect.template = "input_line.select";
InputLineSelect.props = ["value", "possibleVal"];
