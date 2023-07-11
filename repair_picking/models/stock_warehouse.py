# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    repair_steps = fields.Selection(
        [
            ("1_step", "Repair"),
            ("2_steps", "Pick component, repair"),
            ("3_steps", "Pick component, repair, store removed component"),
        ],
        string="Repair Steps",
        default="1_step",
    )
    add_c_type_id = fields.Many2one(
        "stock.picking.type", string="Add Component to Repair"
    )
    remove_c_type_id = fields.Many2one(
        "stock.picking.type", string="Remove component from Repair"
    )
    repair_route_id = fields.Many2one("stock.location.route", string="Repair Route")
    repair_location_id = fields.Many2one("stock.location", string="Repair Location")

    def update_picking_types(self, repair_steps, repair_location_id):
        if repair_steps in ["2_steps", "3_steps"]:
            self.add_c_type_id.active = True
        if repair_steps == "1_step":
            self.add_c_type_id.active = False
        if repair_steps == "3_steps":
            self.remove_c_type_id.active = True
        if repair_steps in ["1_step", "2_steps"]:
            self.remove_c_type_id.active = False
        if repair_location_id:
            self.add_c_type_id.write({"default_location_dest_id": repair_location_id})
            self.remove_c_type_id.write({"default_location_src_id": repair_location_id})

    def update_repair_routes(self, repair_steps, repair_location_id):
        if repair_steps == "2_steps" or repair_steps == "3_steps":
            self.repair_route_id.active = True
            existing_rule = (
                self.env["stock.rule"]
                .with_context(active_test=False)
                .search(
                    [
                        ("picking_type_id", "=", self.add_c_type_id.id),
                        ("route_id", "=", self.repair_route_id.id),
                    ],
                    limit=1,
                )
            )
            existing_rule.active = True
        if repair_steps == "1_step":
            for rule in self.repair_route_id.rule_ids:
                rule.active = False
            self.repair_route_id.active = False
        if repair_location_id:
            self.repair_route_id.rule_ids.filtered(
                lambda r: r.picking_type_id == self.add_c_type_id
            ).write({"location_id": repair_location_id})
            self.repair_route_id.rule_ids.filtered(
                lambda r: r.picking_type_id == self.remove_c_type_id
            ).write({"location_src_id": repair_location_id})
        if repair_steps in ["1_step", "2_steps"]:
            self.repair_route_id.rule_ids.filtered(
                lambda r: r.picking_type_id == self.remove_c_type_id
            ).active = False

    def write(self, vals):
        res = super(StockWarehouse, self).write(vals)
        for warehouse in self:
            repair_steps = vals.get("repair_steps")
            repair_location_id = vals.get("repair_location_id")
            if repair_steps:
                if repair_steps in ["3_steps", "2_steps"]:
                    warehouse._create_repair_picking_types()
                    warehouse._create_repair_route()
                    if repair_steps == "3_steps":
                        warehouse._create_remove_rule()
            if repair_steps or repair_location_id:
                warehouse.update_picking_types(repair_steps, repair_location_id)
                warehouse.update_repair_routes(repair_steps, repair_location_id)
        return res

    def _create_repair_picking_types(self):
        for warehouse in self:
            repair_location_id = (
                warehouse.repair_location_id.id or warehouse.lot_stock_id.id
            )
            if not warehouse.add_c_type_id:
                pbr_type = self.env["stock.picking.type"].create(
                    {
                        "name": "Add Component to Repair",
                        "code": "internal",
                        "sequence_code": "ACR",
                        "warehouse_id": warehouse.id,
                        "default_location_src_id": warehouse.lot_stock_id.id,
                        "default_location_dest_id": repair_location_id,
                        "company_id": warehouse.company_id.id,
                    }
                )
                warehouse.add_c_type_id = pbr_type.id
            else:
                warehouse.add_c_type_id.write(
                    {"default_location_dest_id": repair_location_id}
                )
            if not warehouse.remove_c_type_id:
                par_type = self.env["stock.picking.type"].create(
                    {
                        "name": "Remove component from Repair",
                        "code": "internal",
                        "sequence_code": "RCR",
                        "warehouse_id": warehouse.id,
                        "default_location_src_id": repair_location_id,
                        "default_location_dest_id": warehouse.view_location_id.id,
                        "company_id": warehouse.company_id.id,
                    }
                )
                warehouse.remove_c_type_id = par_type.id
            else:
                warehouse.remove_c_type_id.write(
                    {"default_location_src_id": repair_location_id}
                )

    def _create_repair_route(self):
        for warehouse in self:
            if not warehouse.repair_route_id:
                route = self.env["stock.location.route"].create(
                    {
                        "name": "Repair Route for %s" % warehouse.name,
                        "warehouse_selectable": True,
                        "product_selectable": False,
                        "warehouse_ids": [(6, 0, warehouse.ids)],
                        "company_id": warehouse.company_id.id,
                    }
                )
                warehouse.repair_route_id = route.id
                self.env["stock.rule"].create(
                    {
                        "name": "Add Component to Repair",
                        "picking_type_id": warehouse.add_c_type_id.id,
                        "route_id": route.id,
                        "location_src_id": warehouse.lot_stock_id.id,
                        "location_id": warehouse.repair_location_id.id
                        or warehouse.view_location_id.id,
                        "action": "pull",
                        "company_id": warehouse.company_id.id,
                        "warehouse_id": warehouse.id,
                    }
                )

    def _create_remove_rule(self):
        for warehouse in self:
            existing_rule = (
                self.env["stock.rule"]
                .with_context(active_test=False)
                .search(
                    [
                        ("picking_type_id", "=", warehouse.remove_c_type_id.id),
                        ("route_id", "=", warehouse.repair_route_id.id),
                    ],
                    limit=1,
                )
            )
            if not existing_rule:
                self.env["stock.rule"].create(
                    {
                        "name": "Remove component from Repair",
                        "picking_type_id": warehouse.remove_c_type_id.id,
                        "route_id": warehouse.repair_route_id.id,
                        "location_src_id": warehouse.repair_location_id.id
                        or warehouse.view_location_id.id,
                        "location_id": warehouse.view_location_id.id,
                        "action": "pull",
                        "company_id": warehouse.company_id.id,
                        "warehouse_id": warehouse.id,
                        "active": True,
                    }
                )
            else:
                existing_rule.active = True
