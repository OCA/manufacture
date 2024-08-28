# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import UserError


class RepairOrder(models.Model):
    _inherit = "repair.order"

    @api.model
    def _get_default_location_id(self):
        warehouse = self.env["stock.warehouse"].search(
            [("company_id", "=", self.env.company.id)], limit=1
        )
        return (
            warehouse.repair_location_id.id
            if warehouse and warehouse.repair_location_id
            else False
        )

    # Changing default value on existing field
    location_id = fields.Many2one(
        default=_get_default_location_id,
    )
    procurement_group_id = fields.Many2one(
        "procurement.group", "Procurement Group", copy=False
    )

    def action_repair_cancel(self):
        res = super().action_repair_cancel()
        for picking in self.picking_ids:
            if picking.state not in ["cancel", "done"]:
                picking.action_cancel()
        return res

    def _action_launch_stock_rule(self, repair_lines):
        for line in repair_lines:
            self._run_procurement_repair(line)
        return True

    def _run_procurement_repair(self, line):
        procurements = []
        errors = []
        procurement = self._prepare_procurement_repair(line)
        procurements.append(procurement)
        try:
            self.env["procurement.group"].run(procurements)
        except UserError as error:
            errors.append(error.args[0])
        if errors:
            raise UserError("\n".join(errors))
        return True

    @api.model
    def _get_procurement_data_repair(self, line):
        warehouse = self.location_id.get_warehouse()
        if not self.procurement_group_id:
            group_id = self.env["procurement.group"].create({"name": self.name})
            self.procurement_group_id = group_id
        procurement_data = {
            "name": self.name,
            "group_id": self.procurement_group_id,
            "origin": self.name,
            "date_planned": fields.Datetime.now(),
            "product_id": line.product_id.id,
            "product_qty": line.product_uom_qty,
            "product_uom": line.product_uom.id,
            "company_id": self.company_id,
            "warehouse_id": warehouse,
            "repair_line_id": line.id,
        }
        if line.lot_id:
            procurement_data["lot_id"] = line.lot_id.id
        if line.type == "remove":
            procurement_data[
                "source_repair_location_id"
            ] = line.repair_id.location_id.id
        return procurement_data

    @api.model
    def _prepare_procurement_repair(self, line):
        values = self._get_procurement_data_repair(line)
        warehouse = self.location_id.get_warehouse()
        location = (
            self.location_id
            if line.type == "add"
            else warehouse.remove_c_type_id.default_location_dest_id
        )
        procurement = self.env["procurement.group"].Procurement(
            line.product_id,
            line.product_uom_qty,
            line.product_uom,
            location,
            values.get("origin"),
            values.get("origin"),
            self.company_id,
            values,
        )
        return procurement

    def _update_stock_moves_and_picking_state(self):
        for repair in self:
            for picking in repair.picking_ids:
                if picking.location_dest_id.id == self.location_id.id:
                    for move_line in picking.move_ids_without_package:
                        stock_moves = repair.stock_move_ids.filtered(
                            lambda m: m.product_id.id
                            == repair.operations.filtered(
                                lambda l: l.type == "add"
                                and l.product_id.id == m.product_id.id
                            ).product_id.id
                            and m.location_id.id == self.location_id.id
                        )
                        if stock_moves:
                            stock_moves[0].write(
                                {
                                    "move_orig_ids": [(4, move_line.id)],
                                    "state": "waiting",
                                }
                            )
                if picking.location_id.id == self.location_id.id:
                    for move_line in picking.move_ids_without_package:
                        stock_moves = repair.stock_move_ids.filtered(
                            lambda m: m.product_id.id
                            == repair.operations.filtered(
                                lambda l: l.type == "remove"
                                and l.product_id.id == m.product_id.id
                            ).product_id.id
                            and m.location_dest_id.id == self.location_id.id
                        )
                        if stock_moves:
                            move_line.write(
                                {
                                    "move_orig_ids": [(4, stock_moves[0].id)],
                                    "state": "waiting",
                                }
                            )
                # We are using write here because
                # the repair_stock_move module does not use stock rules.
                # As a result, we manually link the stock moves
                # and then recompute the state of the picking.
                picking._compute_state()

    def action_repair_confirm(self):
        res = super().action_repair_confirm()
        for repair in self:
            warehouse = repair.location_id.get_warehouse()
            if warehouse.repair_steps in ["2_steps", "3_steps"]:
                repair._action_launch_stock_rule(
                    repair.operations.filtered(lambda l: l.type == "add"),
                )
            if warehouse.repair_steps == "3_steps":
                repair._action_launch_stock_rule(
                    repair.operations.filtered(lambda l: l.type == "remove"),
                )
            repair._update_stock_moves_and_picking_state()
        return res

    @api.onchange("location_id")
    def _onchange_location_id(self):
        warehouse = self.location_id.get_warehouse()
        for line in self.operations:
            if line.type == "add":
                line.location_id = self.location_id
            elif line.type == "remove" and warehouse.repair_steps == "3_steps":
                line.location_dest_id = self.location_id


class RepairLine(models.Model):
    _inherit = "repair.line"

    @api.onchange("type", "product_id")
    def onchange_operation_type(self):
        super().onchange_operation_type()
        production_location = self.env["stock.location"].search(
            [("usage", "=", "production")], limit=1
        )
        warehouse = self.repair_id.location_id.get_warehouse()
        if self.type == "add":
            self.write(
                {
                    "location_id": self.repair_id.location_id.id,
                    "location_dest_id": production_location.id,
                }
            )
        elif self.type == "remove":
            self.write({"location_id": production_location.id})
            if warehouse.repair_steps in ["1_step", "2_steps"]:
                scrap_location = self.env["stock.location"].search(
                    [
                        ("scrap_location", "=", True),
                        ("company_id", "=", warehouse.company_id.id),
                    ],
                    limit=1,
                )
                self.write({"location_dest_id": scrap_location.id})
            else:
                self.write({"location_dest_id": self.repair_id.location_id.id})

    def create(self, vals):
        line = super().create(vals)
        if line.repair_id.state in ["confirmed", "under_repair", "ready"]:
            line.repair_id._action_launch_stock_rule(line)
        return line
