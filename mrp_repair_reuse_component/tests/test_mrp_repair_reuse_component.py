# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests import Form, tagged

from odoo.addons.repair.tests.test_repair import TestRepair


@tagged("post_install", "-at_install")
class TestMrpRepairReuseComponent(TestRepair):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.stock_location = cls.stock_warehouse.lot_stock_id
        cls.scrap_location = cls.env["stock.location"].search(
            [
                ("scrap_location", "=", True),
                ("company_id", "=", cls.stock_location.company_id.id),
            ]
        )
        cls.component_serial = cls.env["product.product"].create(
            {"name": "Comp serial", "tracking": "serial"}
        )
        cls.finished_serial = cls.env["product.product"].create(
            {"name": "Finished serial", "tracking": "serial"}
        )
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.finished_serial.product_tmpl_id.id,
                "type": "normal",
                "bom_line_ids": [
                    (0, 0, {"product_id": cls.component_serial.id, "product_qty": 1}),
                ],
            }
        )
        cls.finished_serial_1 = cls._create_serial(cls.finished_serial, "SN0001")
        cls.finished_serial_2 = cls._create_serial(cls.finished_serial, "SN0002")
        cls.finished_serial_3 = cls._create_serial(cls.finished_serial, "SN0003")
        cls.finished_serial_4 = cls._create_serial(cls.finished_serial, "SN0004")
        cls.finished_serial_5 = cls._create_serial(cls.finished_serial, "SN0005")
        cls.component_serial_1 = cls._create_serial(cls.component_serial, "SN0001")
        cls.component_serial_2 = cls._create_serial(cls.component_serial, "SN0002")
        cls.component_serial_3 = cls._create_serial(cls.component_serial, "SN0003")
        cls.component_serial_4 = cls._create_serial(cls.component_serial, "SN0004")
        cls.component_serial_5 = cls._create_serial(cls.component_serial, "SN0005")
        cls.component_serial_6 = cls._create_serial(cls.component_serial, "SN0006")

    @classmethod
    def _create_serial(cls, product, serial_no):
        return cls.env["stock.production.lot"].create(
            {"name": serial_no, "product_id": product.id}
        )

    @classmethod
    def _produce_finished(cls, finished_serial, component_serial):
        mo_form = Form(cls.env["mrp.production"])
        mo_form.product_id = cls.finished_serial
        mo = mo_form.save()
        mo.action_confirm()
        mo_form = Form(mo)
        mo_form.lot_producing_id = finished_serial
        mo_form.save()
        details_operation_form = Form(
            mo.move_raw_ids, view=cls.env.ref("stock.view_stock_move_operations")
        )
        with details_operation_form.move_line_ids.edit(0) as move_line_form:
            move_line_form.lot_id = component_serial
            move_line_form.qty_done = 1
        details_operation_form.save()
        mo.button_mark_done()
        return mo

    @classmethod
    def _repair_switch_component(
        cls, repair_serial, remove_component_serial, add_component_serial, scrap=True
    ):
        repair_form = Form(cls.env["repair.order"])
        repair_form.product_id = cls.finished_serial
        repair_form.lot_id = repair_serial
        with repair_form.operations.new() as repair_line:
            repair_line.type = "add"
            repair_line.product_id = cls.component_serial
            repair_line.lot_id = add_component_serial
            repair_line.product_uom_qty = 1
        with repair_form.operations.new() as repair_line:
            repair_line.type = "remove"
            repair_line.product_id = cls.component_serial
            repair_line.lot_id = remove_component_serial
            repair_line.product_uom_qty = 1
            if not scrap:
                repair_line.location_dest_id = cls.stock_location
        repair = repair_form.save()
        repair.action_validate()
        repair.action_repair_start()
        repair.action_repair_end()
        return repair

    @classmethod
    def _move_product(cls, product, location, location_dest, lot):
        move_form = Form(cls.env["stock.move"])
        move_form.name = "Move product"
        move_form.product_id = product
        move_form.location_id = location
        move_form.location_dest_id = location_dest
        move_form.product_uom = product.uom_id
        move_form.product_uom_qty = 1.0
        move = move_form.save()
        move._action_confirm()
        move_form = Form(move, view=cls.env.ref("stock.view_stock_move_operations"))
        with move_form.move_line_ids.new() as move_line_form:
            move_line_form.lot_id = lot
            move_line_form.qty_done = 1.0
        move_form.save()
        move._action_done()
        return move

    @classmethod
    def _unbuild_product(cls, original_mo, finished_serial):
        unbuild_form = Form(cls.env["mrp.unbuild"])
        unbuild_form.product_id = cls.finished_serial
        unbuild_form.lot_id = finished_serial
        unbuild_form.mo_id = original_mo
        unbuild_order = unbuild_form.save()
        unbuild_order.action_unbuild()
        return unbuild_order

    def test_reuse_component_repair_with_scrap(self):
        # Create Finished 0001 with Component 0001
        self._produce_finished(self.finished_serial_1, self.component_serial_1)
        # Create Finished 0002 with Component 0002
        self._produce_finished(self.finished_serial_2, self.component_serial_2)
        # Create Finished 0003 with Component 0003
        self._produce_finished(self.finished_serial_3, self.component_serial_3)
        # Repair Finished 0001, removing Component 0001 and adding Component 0004
        self._repair_switch_component(
            self.finished_serial_1, self.component_serial_1, self.component_serial_4
        )
        # Move Component 0001 from scrap back to stock
        self._move_product(
            self.component_serial,
            self.scrap_location,
            self.stock_location,
            self.component_serial_1,
        )
        # Repair Finished 0002, removing Component 0002 and adding (reuse) Component 0001
        self._repair_switch_component(
            self.finished_serial_2,
            self.component_serial_2,
            self.component_serial_1,
            scrap=False,
        )
        # Repair Finished 0002, removing Component 0001 and adding Component 0005
        self._repair_switch_component(
            self.finished_serial_2,
            self.component_serial_1,
            self.component_serial_5,
            scrap=False,
        )
        # Repair Finished 0003, removing Component 0003 and adding (reuse) Component 0001
        self._repair_switch_component(
            self.finished_serial_3,
            self.component_serial_3,
            self.component_serial_1,
            scrap=False,
        )
        # Repair Finished 0003, removing Component 0001 and adding Component 0006
        self._repair_switch_component(
            self.finished_serial_3,
            self.component_serial_1,
            self.component_serial_6,
            scrap=False,
        )
        # Create Finished 0004 with Component 0001 (reuse)
        mo_4 = self._produce_finished(self.finished_serial_4, self.component_serial_1)
        # Unbuild Finished 0004
        self._unbuild_product(mo_4, self.finished_serial_4)
        # Create Finished 0005 with Component 0001 (reuse)
        self._produce_finished(self.finished_serial_5, self.component_serial_1)

    def test_reuse_component_repair_without_scrap(self):
        # Create Finished 0001 with Component 0001
        self._produce_finished(self.finished_serial_1, self.component_serial_1)
        # Create Finished 0002 with Component 0002
        self._produce_finished(self.finished_serial_2, self.component_serial_2)
        # Create Finished 0003 with Component 0003
        self._produce_finished(self.finished_serial_3, self.component_serial_3)
        # Repair Finished 0001, removing Component 0001 and adding Component 0004
        self._repair_switch_component(
            self.finished_serial_1,
            self.component_serial_1,
            self.component_serial_4,
            scrap=False,
        )
        # Repair Finished 0002, removing Component 0002 and adding (reuse) Component 0001
        self._repair_switch_component(
            self.finished_serial_2,
            self.component_serial_2,
            self.component_serial_1,
            scrap=False,
        )
        # Repair Finished 0002, removing Component 0001 and adding Component 0005
        self._repair_switch_component(
            self.finished_serial_2,
            self.component_serial_1,
            self.component_serial_5,
            scrap=False,
        )
        # Repair Finished 0003, removing Component 0003 and adding (reuse) Component 0001
        self._repair_switch_component(
            self.finished_serial_3,
            self.component_serial_3,
            self.component_serial_1,
            scrap=False,
        )
        # Repair Finished 0003, removing Component 0001 and adding Component 0006
        self._repair_switch_component(
            self.finished_serial_3,
            self.component_serial_1,
            self.component_serial_6,
            scrap=False,
        )
        # Create Finished 0004 with Component 0001 (reuse)
        mo_4 = self._produce_finished(self.finished_serial_4, self.component_serial_1)
        # Unbuild Finished 0004
        self._unbuild_product(mo_4, self.finished_serial_4)
        # Create Finished 0005 with Component 0001 (reuse)
        self._produce_finished(self.finished_serial_5, self.component_serial_1)
