from odoo import api, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def _get_rule(self, product_id, location_id, values):
        """Override to respect mrp_action from MRP Multi Level wizard."""
        mrp_action = values.get("mrp_action")

        if not mrp_action or mrp_action in ("none", False):
            return super()._get_rule(product_id, location_id, values)

        company = values.get("company_id", self.env.company)
        company_id = company.id if hasattr(company, "id") else company

        domain = [
            ("action", "=", mrp_action),
            ("company_id", "in", [company_id, False]),
        ]

        rule = self.env["stock.rule"].search(
            domain + [("location_dest_id", "=", location_id.id)],
            order="sequence",
            limit=1,
        )

        if not rule:
            warehouse = values.get("warehouse_id")
            if warehouse:
                warehouse_id = warehouse.id if hasattr(warehouse, "id") else warehouse
                rule = self.env["stock.rule"].search(
                    domain + [("warehouse_id", "=", warehouse_id)],
                    order="sequence",
                    limit=1,
                )

        return rule or super()._get_rule(product_id, location_id, values)
