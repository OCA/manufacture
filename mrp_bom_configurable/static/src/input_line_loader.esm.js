/** @odoo-module **/

import {LazyComponent} from "@web/core/assets";
import {registry} from "@web/core/registry";

const {Component, xml} = owl;

class InputLineLoader extends Component {}

InputLineLoader.components = {LazyComponent};
InputLineLoader.template = xml`
<LazyComponent bundle="'mrp_bom_confignominalurable.input_line'" Component="'InputLine'" props="props"/>
`;

registry.category("actions").add("mrp_bom_configurable.input_line", InputLineLoader);
