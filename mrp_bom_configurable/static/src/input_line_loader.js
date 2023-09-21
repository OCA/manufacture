/** @odoo-module **/

import {registry} from "@web/core/registry";
import {LazyComponent} from "@web/core/assets";

const {Component, xml} = owl;

class InputLineLoader extends Component {}

InputLineLoader.components = {LazyComponent};
InputLineLoader.template = xml`
<LazyComponent bundle="'mrp_bom_configurable.input_line'" Component="'InputLine'" props="props"/>
`;

registry.category("actions").add("mrp_bom_configurable.input_line", InputLineLoader);
