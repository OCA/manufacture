# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.fields import Command
from odoo.tests import TransactionCase
from odoo.tests.common import Form


class TestMrpSubcontractingSerialMassProduce(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.subcontractor = cls.env["res.partner"].create(
            {"name": "Test Subcontractor"}
        )
        cls.subcontract_location = cls.subcontractor.property_stock_subcontractor
        cls.comp1 = cls.env["product.product"].create(
            {"name": "Component 1", "type": "product"}
        )
        cls.comp2 = cls.env["product.product"].create(
            {"name": "Component 2", "type": "product"}
        )
        cls.finished = cls.env["product.product"].create(
            {"name": "Finished Product", "type": "product", "tracking": "serial"}
        )
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.finished.product_tmpl_id.id,
                "type": "subcontract",
                "subcontractor_ids": [Command.link(cls.subcontractor.id)],
                "bom_line_ids": [
                    Command.create({"product_id": cls.comp1.id, "product_qty": 1}),
                    Command.create({"product_id": cls.comp2.id, "product_qty": 1}),
                ],
            }
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.comp1, cls.subcontract_location, 10
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.comp2, cls.subcontract_location, 10
        )
        picking_form = Form(cls.env["stock.picking"])
        picking_form.picking_type_id = cls.env.ref("stock.picking_type_in")
        picking_form.partner_id = cls.subcontractor
        with picking_form.move_ids_without_package.new() as move:
            move.product_id = cls.finished
            move.product_uom_qty = 2
        cls.receipt = picking_form.save()
        cls.receipt.action_confirm()

    def _run_mass_produce(self, count=2, starting_serial="SN0001"):
        production = self.receipt.move_ids.move_orig_ids.production_id
        production.action_assign()
        action = production.action_serial_mass_produce_wizard()
        wizard = Form(self.env["stock.assign.serial"].with_context(**action["context"]))
        wizard.next_serial_number = starting_serial
        wizard.next_serial_count = count
        action = wizard.save().generate_serial_numbers_production()
        return Form(self.env["stock.assign.serial"].browse(action["res_id"]))

    def test_mass_produce_auto_records_components(self):
        wizard = self._run_mass_produce()
        wizard.save().apply()
        productions = self.receipt.move_ids.move_orig_ids.production_id.sorted("id")
        self.assertEqual(len(productions), 2)
        self.assertEqual(
            productions.mapped("subcontracting_has_been_recorded"),
            [True, True],
            "Mass Produce should auto-record components for both MOs",
        )
        self.assertEqual(
            productions.mapped("lot_producing_id.name"),
            ["SN0001", "SN0002"],
            "Serial numbers should be assigned to split productions",
        )
        self.assertEqual(
            sorted(self.receipt.move_line_ids.mapped("lot_id.name")),
            ["SN0001", "SN0002"],
            "Serial numbers should be synced to receipt move lines",
        )

    def test_mass_produce_skips_strict_consumption_warning(self):
        # Mass Produce records each split MO with skip_consumption=True, since the
        # consumed qty is set by _split_productions rather than the BoM. Without it,
        # a strict-consumption discrepancy makes subcontracting_record_component
        # return a consumption-wizard action that this automated flow discards,
        # silently leaving the MO unrecorded.
        # Here we fabricate that discrepancy by adding a BoM line after MO creation.
        comp3 = self.env["product.product"].create(
            {"name": "Component 3", "type": "product"}
        )
        self.env["stock.quant"]._update_available_quantity(
            comp3, self.subcontract_location, 10
        )
        self.bom.write(
            {
                "consumption": "strict",
                "bom_line_ids": [
                    Command.create({"product_id": comp3.id, "product_qty": 1})
                ],
            }
        )
        wizard = self._run_mass_produce()
        wizard.save().apply()
        productions = self.receipt.move_ids.move_orig_ids.production_id
        self.assertEqual(len(productions), 2)
        self.assertEqual(
            productions.mapped("subcontracting_has_been_recorded"),
            [True, True],
            "skip_consumption=True should bypass strict BoM consumption "
            "checks so every split MO is recorded",
        )
