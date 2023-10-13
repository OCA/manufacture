from odoo.tests import Form

from odoo.addons.mrp_subcontracting.tests.common import TestMrpSubcontractingCommon


class TestMrpProductionSubcontracting(TestMrpSubcontractingCommon):
    @classmethod
    def setUpClass(cls):
        super(TestMrpProductionSubcontracting, cls).setUpClass()
        cls.comp1_sn = cls.env["product.product"].create(
            {
                "name": "Component1",
                "type": "product",
                "categ_id": cls.env.ref("product.product_category_all").id,
                "tracking": "serial",
            }
        )
        cls.finished_product = cls.env["product.product"].create(
            {
                "name": "finished",
                "type": "product",
                "categ_id": cls.env.ref("product.product_category_all").id,
                "tracking": "lot",
            }
        )
        bom_form = Form(cls.env["mrp.bom"])
        bom_form.type = "subcontract"
        bom_form.subcontractor_ids.add(cls.subcontractor_partner1)
        bom_form.product_tmpl_id = cls.finished_product.product_tmpl_id
        with bom_form.bom_line_ids.new() as bom_line:
            bom_line.product_id = cls.comp1_sn
            bom_line.product_qty = 1
        with bom_form.bom_line_ids.new() as bom_line:
            bom_line.product_id = cls.comp2
            bom_line.product_qty = 1
        cls.bom_tracked = bom_form.save()

    def test_subcontracting_record_component(self):
        """This test uses tracked (serial and lot) component

        and tracked (serial) finished product
        """
        todo_nb = 4
        self.comp2.tracking = "lot"
        self.finished_product.tracking = "serial"

        # Create a receipt picking from the subcontractor
        picking_form = Form(self.env["stock.picking"])
        picking_form.picking_type_id = self.env.ref("stock.picking_type_in")
        picking_form.partner_id = self.subcontractor_partner1
        with picking_form.move_ids_without_package.new() as move:
            move.product_id = self.finished_product
            move.product_uom_qty = todo_nb
        picking_receipt = picking_form.save()
        picking_receipt.action_confirm()

        self.assertTrue(
            picking_receipt.display_action_record_components,
            msg="We should be able to call the 'record_components' button",
        )

        # Check the created manufacturing order
        mo = self.env["mrp.production"].search([("bom_id", "=", self.bom_tracked.id)])
        result = mo._check_exception_subcontracting_record_component()
        self.assertDictEqual(result, {"type": "ir.actions.act_window_close"})
        self.assertFalse(mo._has_been_recorded())
        self.assertEqual(len(mo), 1)
        self.assertEqual(len(mo.picking_ids), 0)
        wh = picking_receipt.picking_type_id.warehouse_id
        self.assertEqual(mo.picking_type_id, wh.subcontracting_type_id)
        self.assertFalse(mo.picking_type_id.active)

        # Create a RR
        pg1 = self.env["procurement.group"].create({})
        self.env["stock.warehouse.orderpoint"].create(
            {
                "name": "xxx",
                "product_id": self.comp1_sn.id,
                "product_min_qty": 0,
                "product_max_qty": 0,
                "location_id": self.env.user.company_id.subcontracting_location_id.id,
                "group_id": pg1.id,
            }
        )

        # Run the scheduler and check the created picking
        self.env["procurement.group"].run_scheduler()
        picking = self.env["stock.picking"].search([("group_id", "=", pg1.id)])
        self.assertEqual(len(picking), 1)
        self.assertEqual(picking.picking_type_id, wh.out_type_id)

        lot_comp2 = self.env["stock.production.lot"].create(
            {
                "name": "lot_comp2",
                "product_id": self.comp2.id,
                "company_id": self.env.company.id,
            }
        )
        serials_finished = []
        serials_comp1 = []
        for i in range(todo_nb):
            serials_finished.append(
                self.env["stock.production.lot"].create(
                    {
                        "name": "serial_fin_%s" % i,
                        "product_id": self.finished_product.id,
                        "company_id": self.env.company.id,
                    }
                )
            )
            serials_comp1.append(
                self.env["stock.production.lot"].create(
                    {
                        "name": "serials_comp1_%s" % i,
                        "product_id": self.comp1_sn.id,
                        "company_id": self.env.company.id,
                    }
                )
            )

        mo_ids = self.env["mrp.production"]
        for i in range(todo_nb):
            action = picking_receipt.action_record_components()
            mo = self.env["mrp.production"].browse(action["res_id"])
            mo_form = Form(mo.with_context(**action["context"]), view=action["view_id"])
            mo_form.lot_producing_id = serials_finished[i]
            mo_form.qty_producing = 1
            with mo_form.move_line_raw_ids.edit(0) as ml:
                self.assertEqual(ml.product_id, self.comp1_sn)
                ml.lot_id = serials_comp1[i]
            with mo_form.move_line_raw_ids.edit(1) as ml:
                self.assertEqual(ml.product_id, self.comp2)
                ml.lot_id = lot_comp2
            mo = mo_form.save()
            mo.subcontracting_record_component()
            mo_ids |= mo
            self.assertTrue(mo._has_been_recorded())

        self.assertFalse(
            picking_receipt.display_action_record_components,
            msg="We should not be able to call the 'record_components' button",
        )

        picking_receipt.button_validate()
        self.assertEqual(mo.state, "done")
        self.assertEqual(
            mo.procurement_group_id.mrp_production_ids.mapped("state"),
            ["done"] * todo_nb,
        )
        self.assertEqual(len(mo.procurement_group_id.mrp_production_ids), todo_nb)
        self.assertEqual(
            mo.procurement_group_id.mrp_production_ids.mapped("qty_produced"),
            [1] * todo_nb,
        )

        # Available quantities should be negative at the
        # subcontracting location for each components
        avail_qty_comp1 = self.env["stock.quant"]._get_available_quantity(
            self.comp1_sn,
            self.subcontractor_partner1.property_stock_subcontractor,
            allow_negative=True,
        )
        avail_qty_comp2 = self.env["stock.quant"]._get_available_quantity(
            self.comp2,
            self.subcontractor_partner1.property_stock_subcontractor,
            allow_negative=True,
        )
        avail_qty_finished = self.env["stock.quant"]._get_available_quantity(
            self.finished_product, wh.lot_stock_id
        )
        self.assertEqual(avail_qty_comp1, -todo_nb)
        self.assertEqual(avail_qty_comp2, -todo_nb)
        self.assertEqual(avail_qty_finished, todo_nb)
