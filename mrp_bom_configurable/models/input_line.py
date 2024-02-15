from odoo import api, fields, models


class Inputline(models.Model):
    _name = "input.line"
    _description = "Line configuration scenari"

    name = fields.Char()
    sequence = fields.Integer()
    bom_id = fields.Many2one(
        comodel_name="mrp.bom", required=True, related="config_id.bom_id"
    )
    config_id = fields.Many2one(comodel_name="input.config", required=True)
    alert = fields.Text(help="Outside limit configuration is reported here")
    checked = fields.Boolean(
        compute="_compute_check",
        store=True,
        help="If checked, the configuration have been evaluate",
    )
    comment = fields.Text()
    bom_data_preview = fields.Json()

    def _get_config_elements(self):
        raise NotImplementedError(
            "_get_config_elements must be overriden and"
            + " return the specific fields in the input line"
        )

    def ui_clone(self):
        self.ensure_one()
        vals = {"name": "%s copy" % self.name}
        self.copy(vals)

    def _get_filtered_components_from_values(self):
        elements = dict()
        conf_names = dict()
        for elm in self._get_config_elements():
            if self._fields[elm].type == "many2one":
                value = self[elm].display_name
            else:
                value = self[elm]
            elements[elm] = value
            conf_names[self._fields[elm].string] = value
        lines = self.bom_id.check_domain(elements)
        return lines, conf_names

    def get_values_with_field_desc(self):
        self.ensure_one()
        values = [
            {
                "name": "name",
                "string": "Name",
                "value": self.name,
            }
        ]
        for field in self._get_config_elements():
            field_vals = {
                "name": field,
                "string": self._fields[field].string,
                "type": self._fields[field].type,
            }

            if self._fields[field].type == "many2one":
                fieldinfo = self._fields[field]
                field_vals["value"] = self[field].id
                field_vals["display_name"] = self[field].display_name
                field_vals["model"] = fieldinfo.comodel_name
                if isinstance(fieldinfo.domain, list) or fieldinfo.domain is None:
                    field_vals["domain"] = fieldinfo.domain
                else:
                    field_vals["domain"] = fieldinfo.domain(self)
            else:
                field_vals["value"] = self[field]

            if self._fields[field].type == "selection":
                if self._fields[field].related:
                    field_vals["possible_values"] = self._fields[field].selection(self)
                else:
                    field_vals["possible_values"] = self._fields[field].selection

            values.append(field_vals)

        return values

    def check_one_data(self):
        pass

    def _create_report_dict_from_line(self, line):
        return {
            "id": line.id,
            "component": line.product_id.display_name,
            "quantity": line.product_qty,
            "unit": line.product_uom_id.display_name,
        }

    def _create_bom_data_preview(self):
        self.ensure_one()
        lines, conf_names = self._get_filtered_components_from_values()
        return {
            "config_data": [
                {"name": key, "display_name": conf_names[key]} for key in conf_names
            ],
            "data": [self._create_report_dict_from_line(line) for line in lines],
        }

    def populate_bom_data_preview(self):
        self.bom_data_preview = self._create_bom_data_preview()

    def get_json(self):
        self.ensure_one()
        self.populate_bom_data_preview()
        return self.bom_data_preview

    def open_form_pop_up(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Input line information",
            "res_model": "input.line",
            "view_mode": "form",
            "target": "new",
            "res_id": self.id,
        }

    def create_bom_from_line(self):
        self.ensure_one()
        components, _ = self._get_filtered_components_from_values()
        new_bom_lines = []
        price = 0

        if len(self.configured_bom_id) == 0:
            new_product = self.env["product.template"].create(
                {
                    "name": f"{self.config_id.name} - {self.name}",
                }
            )
            new_bom = self.env["mrp.bom"].create(
                {
                    "configuration_type": "configured",
                    "product_qty": 1,
                    "product_tmpl_id": new_product.id,
                }
            )

            self.configured_bom_id = new_bom.id
        else:
            self.configured_bom_id.bom_line_ids.unlink()

        for comp in components:
            quantity = (
                comp.compute_qty_from_formula(self)
                if comp.use_formula_compute_qty
                else comp.product_qty
            )
            quantity *= self.count
            price += quantity * comp.product_id.lst_price
            new_bom_line = self.env["mrp.bom.line"].create(
                {
                    "product_tmpl_id": comp.product_tmpl_id.id,
                    "product_id": comp.product_id.id,
                    "product_qty": quantity,
                    "bom_id": self.configured_bom_id.id,
                }
            )
            new_bom_lines.append(new_bom_line.id)

        self.configured_bom_id.product_tmpl_id.product_variant_id.lst_price = price

    def action_show_configured_bom(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "mrp.bom.configured",
            "view_mode": "form",
            "view_id": self.env.ref("mrp_bom_configurable.mrp_bom_configured_form").id,
            "target": "new",
        }

    @api.depends("bom_id")
    def _compute_check(self):
        "You need to override this method in your custom config to trigger adhoc checks"
