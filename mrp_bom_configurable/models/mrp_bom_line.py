from odoo import fields, models
from odoo.tools.safe_eval import safe_eval


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    domain = fields.Text(help="Odoo syntax domain only")
    condition = fields.Text(help="Comment explaining domain if needed")

    def goto_configurable_bom_report(self):
        self.ensure_one()
        # TODO add button
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        url = "%s/report/html/mrp_bom_configurable.report_bom_configurable/%s" % (
            base_url,
            self.id,
        )
        return {
            "model": "ir.actions._act_url",
            "name": self.name,
            "url": url,
            "target": "new",
        }

    def execute_domain_element(self, element, values):
        param, operator, value = element
        code = f"{repr(values[param])} {operator} {repr(value)}"

        return safe_eval(code)

    def execute_domain(self, domain, values):
        if domain[0] == "OR":
            return any(
                self.execute_domain(domain_elm, values) for domain_elm in domain[1:]
            )
        elif isinstance(domain, list):
            return all(self.execute_domain(domain_elm, values) for domain_elm in domain)
        else:
            return self.execute_domain_element(domain, values)

    def execute(self, values):
        self.ensure_one()
        if not self.domain:
            return True
        else:
            domain = safe_eval(self.domain)

            return self.execute_domain(domain, values)
