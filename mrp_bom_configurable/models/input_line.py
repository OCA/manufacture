from odoo import api, fields, models


class Inputline(models.Model):
    _name = "input.line"
    _description = "Line configuration scenari"

    name = fields.Char()
    sequence = fields.Integer()
    bom_id = fields.Many2one(
        comodel_name="mrp.bom",
        required=True,
    )
    config_id = fields.Many2one(comodel_name="input.config", required=True)
    count = fields.Integer(default=1)
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

    def _get_lines(self):
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

    def check_one_data():
        pass

    def ui_configure(self):
        # TODO
        self.ensure_one()
        lines, conf_names = self._get_lines()
        self.bom_data_preview = {
            "config_data": [
                {"name": key, "display_name": conf_names[key]} for key in conf_names
            ],
            "data": [
                {
                    "id": line.id,
                    "component": line.product_id.display_name,
                    "quantity": line.product_qty,
                    "unit": line.product_uom_id.display_name,
                }
                for line in lines
            ],
        }

    def get_json(self):
        if self.bom_data_preview is None:
            self.ui_configure()
        return self.bom_data_preview

    @api.depends("bom_id", "count")
    def _compute_check(self):
        "You need to override this method in your custom config to trigger adhoc checks"
