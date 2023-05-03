# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class MrpComponentOperate(models.Model):
    _name = "mrp.component.operate"
    _description = "Component Operate"

    product_id = fields.Many2one("product.product", required=True)

    tracking = fields.Selection(
        string="Product Tracking", readonly=True, related="product_id.tracking"
    )

    product_qty = fields.Float(
        "Quantity", default=1.0, required=True, digits="Product Unit of Measure"
    )

    lot_id = fields.Many2one("stock.production.lot")

    mo_id = fields.Many2one("mrp.production", ondelete="cascade", required=True)

    operation_id = fields.Many2one("mrp.component.operation", required=True)

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
            move = self.mo_id.move_raw_ids.filtered(
                lambda x: x.product_id == self.product_id
            )
            filtered_pickings = self.mo_id.picking_ids.filtered(
                lambda x: x.location_dest_id == self.operation_id.source_location_id
            )
            move.move_orig_ids |= filtered_pickings[-1].move_ids_without_package
        elif self.incoming_operation == "no":
            res = []
        return res

    @api.model
    def _domain_for_available_quants(self, move):
        return [
            ("location_id", "child_of", move.location_id.id),
            ("product_id", "=", move.product_id.id),
            ("quantity", ">", 0),
        ]

    @api.model
    def _get_available_quants(self, move):
        domain = self._domain_for_available_quants(move)
        return self.env["stock.quant"].search(domain)

    def _run_outgoing_operations(self):
        res = []
        if self.outgoing_operation == "scrap":
            move = self.mo_id.move_raw_ids.filtered(
                lambda x: x.product_id == self.product_id
            )
            available_quants = self._get_available_quants(move)
            initial_quantities = {
                quant.lot_id: quant.quantity for quant in available_quants
            }
            res = self._create_scrap()
            updated_quants = self._get_available_quants(move)
            initial_quantity = initial_quantities.get(self.lot_id)
            updated_quant = updated_quants.filtered(lambda q: q.lot_id == self.lot_id)
            if updated_quant:
                updated_quant = updated_quant[0]
                if (
                    initial_quantity is not None
                    and updated_quant.quantity == initial_quantity
                ):
                    new_quantity = initial_quantity - self.product_qty
                    updated_quant._update_available_quantity(
                        self.product_id.id,
                        self.operation_id.source_location_id.id,
                        new_quantity,
                        lot_id=self.lot_id.id,
                    )
        elif self.outgoing_operation == "move":
            res = self._run_procurement(
                self.operation_id.destination_route_id,
                self.operation_id.destination_location_id,
            )
            move = self.mo_id.move_raw_ids.move_line_ids.filtered(
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

    def _create_scrap(self):
        scrap = self.env["stock.scrap"].create(
            {
                "origin": self.mo_id.name,
                "product_id": self.product_id.id,
                "lot_id": self.lot_id.id,
                "scrap_qty": self.product_qty,
                "product_uom_id": self.product_id.product_tmpl_id.uom_id.id,
                "location_id": self.operation_id.source_location_id.id,
                "scrap_location_id": self.operation_id.scrap_location_id.id,
                "create_date": fields.Datetime.now(),
                "company_id": self.env.company.id,
            }
        )
        self.mo_id.scrap_ids |= scrap
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
    def _get_procurement_data(self, route, dest_location):
        if not route:
            raise ValidationError(_("No route specified"))
        procurement_data = {
            "name": self.mo_id and self.mo_id.name,
            "group_id": self.mo_id.procurement_group_id,
            "origin": self.mo_id.name,
            "date_planned": fields.Datetime.now(),
            "product_id": self.product_id.id,
            "product_qty": self.product_qty,
            "product_uom": self.product_id.product_tmpl_id.uom_id.id,
            "location_id": dest_location.id,
            "route_ids": route,
            "company_id": self.env.company.id,
            "mrp_production_ids": self.mo_id.id,
        }
        if self.lot_id and route != self.operation_id.source_route_id:
            procurement_data["lot_id"] = self.lot_id.id
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
