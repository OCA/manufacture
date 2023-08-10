from odoo import fields, models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    condition = fields.Text(
        help="Mettre ici sous quelles conditions le composant sera "
        "utilisé pour la configuration"
    )
    domain = fields.Text(help="Odoo syntax domain only")

    def goto_variable_bom_report(self):
        self.ensure_one()
        # TODO add button
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        url = "%s/report/html/mrp_bom_variable.report_bom_variable/%s" % (
            base_url,
            self.id,
        )
        return {
            "model": "ir.actions._act_url",
            "name": self.name,
            "url": url,
            "target": "new",
        }
