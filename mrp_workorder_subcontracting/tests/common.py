from odoo import Command
from odoo.tests.common import TransactionCase


class WorkorderSubcontractingCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.fixed_date = "2026-01-15 10:00:00"
        cls.company = cls.env.company
        cls.unit = cls.env.ref("uom.product_uom_unit")
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.stock_location = cls.warehouse.lot_stock_id
        cls.subcontract_location = cls.env.ref(
            "mrp_workorder_subcontracting.stock_location_subcontractors_general"
        )
        cls.virtual_subcontract_location = cls.env.ref(
            "mrp_workorder_subcontracting.stock_location_virtual_subcontract"
        )
        cls.virtual_finished_location = cls.env.ref(
            "mrp_workorder_subcontracting."
            "stock_location_virtual_finished_subcontract"
        )
        cls.parts_out_type = cls.env.ref(
            "mrp_workorder_subcontracting.subcontracting_picking_type_parts_out"
        )
        cls.parts_in_type = cls.env.ref(
            "mrp_workorder_subcontracting.subcontracting_picking_type_parts_in"
        )
        cls.finished_out_type = cls.env.ref(
            "mrp_workorder_subcontracting.subcontracting_picking_type_finished_out"
        )
        cls.finished_in_type = cls.env.ref(
            "mrp_workorder_subcontracting.subcontracting_picking_type_finished_in"
        )
        cls.env.user.groups_id = [
            Command.link(
                cls.env.ref("mrp_workorder_subcontracting.group_flow_type_urgent").id
            ),
            Command.link(
                cls.env.ref(
                    "mrp_workorder_subcontracting."
                    "group_flow_type_subcontractor_stock"
                ).id
            ),
        ]
        cls.po_type = cls.env.ref("mrp_workorder_subcontracting.po_type_subcontracting")
        cls.po_type_instant = cls.env.ref(
            "mrp_workorder_subcontracting.po_type_subcontracting_instant_return"
        )
        cls._configure_warehouse()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Subcontractor",
                "property_stock_subcontract_location_id": cls.subcontract_location.id,
                "property_stock_virtual_subcontract_location_id": (
                    cls.virtual_subcontract_location.id
                ),
            }
        )
        cls.other_partner = cls.env["res.partner"].create(
            {
                "name": "Second Test Subcontractor",
                "property_stock_subcontract_location_id": cls.subcontract_location.id,
                "property_stock_virtual_subcontract_location_id": (
                    cls.virtual_subcontract_location.id
                ),
            }
        )
        cls.service = cls.env["product.product"].create(
            {
                "name": "Subcontracting Service",
                "type": "service",
                "purchase_ok": True,
                "uom_id": cls.unit.id,
                "uom_po_id": cls.unit.id,
            }
        )
        cls.component = cls.env["product.product"].create(
            {
                "name": "Subcontracting Component",
                "is_storable": True,
                "uom_id": cls.unit.id,
                "uom_po_id": cls.unit.id,
            }
        )
        cls.finished_parts = cls.env["product.product"].create(
            {
                "name": "Finished Product With Parts Flow",
                "is_storable": True,
                "uom_id": cls.unit.id,
                "uom_po_id": cls.unit.id,
            }
        )
        cls.finished_virtual = cls.env["product.product"].create(
            {
                "name": "Finished Product With Finished Flow",
                "is_storable": True,
                "uom_id": cls.unit.id,
                "uom_po_id": cls.unit.id,
            }
        )
        cls.parts_bom = cls._create_bom(subcontract_parts=True)
        cls.finished_bom = cls._create_bom(subcontract_parts=False)

    @classmethod
    def _configure_warehouse(cls):
        cls.warehouse.write(
            {
                "sub_out_picking_type_id": cls.parts_out_type.id,
                "sub_in_picking_type_id": cls.parts_in_type.id,
                "sub_out_virtual_picking_type_id": cls.finished_out_type.id,
                "sub_in_virtual_picking_type_id": cls.finished_in_type.id,
            }
        )

    @classmethod
    def _create_bom(cls, subcontract_parts=True):
        product = cls.finished_parts if subcontract_parts else cls.finished_virtual
        bom_values = {
            "product_id": product.id,
            "product_tmpl_id": product.product_tmpl_id.id,
            "product_uom_id": cls.unit.id,
            "product_qty": 1.0,
            "type": "normal",
            "operation_ids": [
                Command.create(
                    {
                        "name": (
                            "Subcontract Parts Operation"
                            if subcontract_parts
                            else "Subcontract Finished Operation"
                        ),
                        "workcenter_id": cls.env.ref("mrp.mrp_workcenter_3").id,
                        "subcontract_ok": True,
                        "subcontractor_partner_ids": [
                            Command.set((cls.partner | cls.other_partner).ids)
                        ],
                        "subcontract_product_id": cls.service.id,
                    }
                )
            ],
        }
        if subcontract_parts:
            bom_values["bom_line_ids"] = [
                Command.create(
                    {
                        "product_id": cls.component.id,
                        "product_qty": 2.0,
                        "product_uom_id": cls.unit.id,
                    }
                )
            ]
        bom = cls.env["mrp.bom"].create(bom_values)
        if subcontract_parts:
            bom.bom_line_ids.operation_id = bom.operation_ids[:1]
        return bom

    def _create_production(self, subcontract_parts=True, qty=10.0):
        bom = self.parts_bom if subcontract_parts else self.finished_bom
        product = self.finished_parts if subcontract_parts else self.finished_virtual
        production = self.env["mrp.production"].create(
            {
                "product_id": product.id,
                "product_uom_id": self.unit.id,
                "product_qty": qty,
                "bom_id": bom.id,
                "picking_type_id": self.warehouse.manu_type_id.id,
            }
        )
        production.action_confirm()
        self.assertTrue(production.workorder_ids)
        return production

    def _get_workorder(self, subcontract_parts=True, qty=10.0):
        return self._create_production(
            subcontract_parts=subcontract_parts, qty=qty
        ).workorder_ids[:1]

    def _create_standard_wizard(
        self, workorders, partner=None, purchase_type=None, service=None
    ):
        return self.env["mrp.workorder.assign.subcontract"].create(
            {
                "workorder_ids": [Command.set(workorders.ids)],
                "partner_ids": [Command.set((partner or self.partner).ids)],
                "date_finished": self.fixed_date,
                "flow_type": "standard",
                "create_purchase_order": True,
                "type_id": (purchase_type or self.po_type).id,
                "service_id": (service or self.service).id,
            }
        )

    def _assign_standard_purchase_order(self, workorders, purchase_type=None):
        wizard = self._create_standard_wizard(workorders, purchase_type=purchase_type)
        wizard.assign()
        purchase_order = workorders.purchase_order_line_ids.order_id
        self.assertEqual(len(purchase_order), 1)
        return purchase_order

    def _confirm_standard_purchase_order(self, workorders, purchase_type=None):
        purchase_order = self._assign_standard_purchase_order(
            workorders, purchase_type=purchase_type
        )
        purchase_order.with_context(skip_subcontract_bid_wizard=True).button_confirm()
        self.assertEqual(purchase_order.state, "purchase")
        return purchase_order

    def _create_stock_wizard(
        self, workorders, flow_type, partner=None, service=None, urgent_note=None
    ):
        values = {
            "workorder_ids": [Command.set(workorders.ids)],
            "partner_ids": [Command.set((partner or self.partner).ids)],
            "date_finished": self.fixed_date,
            "flow_type": flow_type,
            "service_id": (service or self.service).id,
        }
        if urgent_note:
            values["urgent_note"] = urgent_note
        return self.env["mrp.workorder.assign.subcontract"].create(values)

    def _assign_stock_flow(
        self, workorders, flow_type, partner=None, service=None, urgent_note=None
    ):
        wizard = self._create_stock_wizard(
            workorders,
            flow_type,
            partner=partner,
            service=service,
            urgent_note=urgent_note,
        )
        wizard.assign()
        return wizard

    def _make_available(self, product, location, quantity):
        self.env["stock.quant"]._update_available_quantity(product, location, quantity)

    def _validate_picking(self, picking, qty_by_move=None, cancel_backorder=False):
        qty_by_move = qty_by_move or {}
        for move in picking.move_ids.filtered(lambda move: move.state != "cancel"):
            move.quantity = qty_by_move.get(move.id, move.product_uom_qty)
            move.picked = True
        picking.with_context(cancel_backorder=cancel_backorder)._action_done()
        picking.invalidate_recordset()
        return self.env["stock.picking"].search([("backorder_id", "=", picking.id)])
