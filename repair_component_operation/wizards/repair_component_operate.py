# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class RepairComponentOperate(models.Model):
    _name = "repair.component.operate"
    _description = "Component Operate"

    product_id = fields.Many2one("product.product", required=True)

    tracking = fields.Selection(
        string="Product Tracking", readonly=True, related="product_id.tracking"
    )

    product_qty = fields.Float(
        "Quantity", default=1.0, required=True, digits="Product Unit of Measure"
    )

    lot_id = fields.Many2one("stock.production.lot")

    repair_id = fields.Many2one("repair.order", ondelete="cascade", required=True)

    operation_id = fields.Many2one(
        "repair.component.operation",
        required=True,
    )

    incoming_operation = fields.Selection(
        related="operation_id.incoming_operation",
        required=True,
    )

    outgoing_operation = fields.Selection(
        related="operation_id.outgoing_operation",
        required=True,
    )

    @api.onchange("operation_id")
    def _onchange_operation_id(self):
        for rec in self:
            rec.incoming_operation = rec.operation_id.incoming_operation
            rec.outgoing_operation = rec.operation_id.outgoing_operation

    def _run_incoming_operations(self):
        res = []
        if self.incoming_operation == "replace":
            res = self._run_procurement(
                self.operation_id.source_route_id, self.operation_id.source_location_id
            )
            move = self.repair_id.operations.move_id.filtered(
                lambda x: x.product_id == self.product_id
            )
            filtered_pickings = self.repair_id.picking_ids.filtered(
                lambda x: x.location_dest_id == self.operation_id.source_location_id
            )
            move.move_orig_ids |= filtered_pickings[-1].move_ids_without_package
            self.repair_id.operations.filtered(
                lambda rl: rl.lot_id == self.lot_id and rl.type == "add"
            ).lot_id = False
        elif self.incoming_operation == "no":
            res = []
        return res

    def _run_outgoing_operations(self):
        res = []
        if self.outgoing_operation == "scrap":
            res = self._create_scrap()
        elif self.outgoing_operation == "move":
            res = self._run_procurement(
                self.operation_id.destination_route_id,
                self.operation_id.destination_location_id,
            )
            move = self.repair_id.operations.move_id.move_line_ids.filtered(
                lambda x: x.product_id == self.product_id
                and (x.lot_id == self.lot_id or self.lot_id is False)
            )
            if move.product_uom_qty == self.product_qty:
                move.unlink()
            else:
                move.write(
                    {
                        "product_uom_qty": (move.product_uom_qty - self.product_qty),
                    }
                )
                move.move_id._recompute_state()
        elif self.outgoing_operation == "no":
            res = []
        return res

    def _create_scrap_vals(self):
        return {
            "origin": self.repair_id.name,
            "product_id": self.product_id.id,
            "lot_id": self.lot_id.id,
            "scrap_qty": self.product_qty,
            "product_uom_id": self.product_id.product_tmpl_id.uom_id.id,
            "location_id": self.operation_id.source_location_id.id,
            "scrap_location_id": self.operation_id.scrap_location_id.id,
            "company_id": self.env.company.id,
            "repair_id": self.repair_id.id,
        }

    def _create_scrap(self):
        scrap = self.env["stock.scrap"].create(self._create_scrap_vals())
        scrap.action_validate()
        return scrap

    def _run_procurement(self, route, dest_location):
        """Method called when the user clicks on create picking"""
        procurements = []
        errors = []
        procurement = self._prepare_procurement(route, dest_location)
        procurements.append(procurement)
        try:
            self.env["procurement.group"].run(procurements)
        except UserError as error:
            errors.append(error.args[0])
        if errors:
            raise UserError("\n".join(errors))
        return procurements

    @api.model
    def _prepare_procurement_group_vals(self, values):
        return {"name": values["name"]}

    @api.model
    def _get_procurement_data(self, route, dest_location):
        if not route:
            raise ValidationError(_("No route specified"))
        repair_line = self.repair_id.operations.filtered(
            lambda rl: rl.type == "add"
            and rl.product_id == self.product_id
            and rl.lot_id == self.lot_id
        )
        procurement_data = {
            "name": self.repair_id and self.repair_id.name,
            "origin": self.repair_id.name,
            "date_planned": fields.Datetime.now(),
            "product_id": self.product_id.id,
            "product_qty": self.product_qty,
            "product_uom": self.product_id.product_tmpl_id.uom_id.id,
            "location_id": dest_location.id,
            "route_ids": route,
            "company_id": self.env.company.id,
            "repair_id": self.repair_id.id,
            "repair_line_id": repair_line[0].id
            if len(repair_line) > 1
            else repair_line.id,
        }
        if self.lot_id and route != self.operation_id.source_route_id:
            procurement_data["lot_id"] = self.lot_id.id
        group_id = self.env["procurement.group"].search(
            [("name", "=", procurement_data["name"])]
        )
        if not group_id:
            group_id = self.env["procurement.group"].create(
                self._prepare_procurement_group_vals(procurement_data)
            )
        procurement_data["group_id"] = group_id
        return procurement_data

    @api.model
    def _prepare_procurement(self, route, dest_location):
        values = self._get_procurement_data(route, dest_location)
        procurement = self.env["procurement.group"].Procurement(
            self.product_id,
            self.product_qty,
            self.product_id.product_tmpl_id.uom_id,
            dest_location,
            values.get("origin"),
            values.get("origin"),
            self.env.company,
            values,
        )
        return procurement

    def action_operate_component(self):
        self._run_outgoing_operations()
        self._run_incoming_operations()
        return
