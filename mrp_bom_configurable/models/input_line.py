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

    def _create_vals_for_copy(self):
        vals = {"name": "%s copy" % self.name}
        return vals

    def ui_clone(self):
        self.ensure_one()
        vals = self._create_vals_for_copy()
        self.copy(vals)

    def _get_input_line_values(self):
        elements = dict()
        for elm in self._get_config_elements():
            if self._fields[elm].type == "many2one":
                value = self[elm].display_name
            else:
                value = self[elm]
            elements[elm] = value
        return elements

    def check_one_data(self):
        pass

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

    def create_bom_line_data(self):
        self.ensure_one()
        components = self.bom_id.get_bom_configured_data(self)
        bom_lines_data = []

        for comp in components:
            bom_line_data = {
                "product_tmpl_id": comp["line"].product_tmpl_id,
                "product_id": comp["line"].product_id,
                "product_qty": comp["product_qty"],
            }
            bom_lines_data.append(bom_line_data)

        return bom_lines_data

    def action_show_configured_bom(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "mrp.bom.configured",
            "view_mode": "form",
            "view_id": self.env.ref(
                "mrp_bom_configurable.mrp_bom_configured_form_view"
            ).id,
            "target": "new",
            "context": f"{{'active_id': {self.id}}}",
        }

    @api.depends("bom_id")
    def _compute_check(self):
        "You need to override this method in your custom config to trigger adhoc checks"
