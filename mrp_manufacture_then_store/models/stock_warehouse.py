# Copyright 2026 Melvin Diabat @ OpenITech
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models
from odoo.exceptions import UserError


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    manufacture_steps = fields.Selection(
        selection_add=[("ms", "Manufacture then store products (2 steps)")],
        ondelete={"ms": "set default"},
    )

    def write(self, vals):
        new_step = vals.get("manufacture_steps")
        if new_step not in ("mrp_one_step", "pbm"):
            return super().write(vals)

        warehouses = self.filtered(
            lambda warehouse: warehouse.manufacture_steps == "ms"
        )
        if not warehouses:
            return super().write(vals)

        locations = warehouses.mapped("sam_loc_id")
        if new_step == "mrp_one_step":
            locations |= warehouses.mapped("pbm_loc_id")
        if locations:
            child_locations = (
                self.env["stock.location"]
                .with_context(active_test=False)
                .search([("id", "child_of", locations.ids), ("active", "=", True)])
            )
            location_domain = [
                ("state", "not in", ("done", "cancel")),
                "|",
                ("location_id", "in", child_locations.ids),
                ("location_dest_id", "in", child_locations.ids),
            ]
            if self.env["stock.move"].search_count(
                location_domain, limit=1
            ) or self.env["stock.move.line"].search_count(location_domain, limit=1):
                raise UserError(
                    self.env._(
                        "Finish or cancel stock operations involving Pre-Production "
                        "or Post-Production before changing the manufacturing steps."
                    )
                )

        # Native stock.location.write checks quants; keep its effects atomic on error.
        with self.env.cr.savepoint():
            return super().write(vals)

    def get_rules_dict(self):
        rules = super().get_rules_dict()
        for warehouse in self:
            # Select Odoo's SAM push independently of the 3-step rule order.
            rules[warehouse.id]["ms"] = [
                routing
                for routing in rules[warehouse.id]["pbm_sam"]
                if routing.from_loc == warehouse.sam_loc_id
                and routing.dest_loc == warehouse.lot_stock_id
                and routing.picking_type == warehouse.sam_type_id
                and routing.action == "push"
            ]
        return rules

    def _get_route_name(self, route_type):
        if route_type == "ms":
            return self.env._("Manufacture then store products (2 steps)")
        return super()._get_route_name(route_type)

    def _get_locations_values(self, vals, code=False):
        values = super()._get_locations_values(vals, code=code)
        manufacture_steps = vals.get("manufacture_steps") or (
            self[0].manufacture_steps if self else False
        )
        if manufacture_steps == "ms":
            values["sam_loc_id"]["active"] = True
        return values

    def _update_location_manufacture(self, new_manufacture_step):
        if new_manufacture_step == "ms":
            # Reuse Post-Production without archiving stocked locations.
            self.mapped("sam_loc_id").write({"active": True})
            return None
        return super()._update_location_manufacture(new_manufacture_step)

    def _get_picking_type_update_values(self):
        values = super()._get_picking_type_update_values()
        if self.manufacture_steps == "ms":
            values["sam_type_id"]["active"] = bool(
                self.manufacture_to_resupply and self.active
            )
            values["manu_type_id"]["default_location_src_id"] = self.lot_stock_id.id
            values["manu_type_id"]["default_location_dest_id"] = self.sam_loc_id.id
        return values

    def _generate_global_route_rules_values(self):
        values = super()._generate_global_route_rules_values()
        if self.manufacture_steps == "ms":
            values["pbm_mto_pull_id"]["update_values"]["active"] = False
            values["manufacture_pull_id"]["update_values"]["propagate_cancel"] = True
        return values
