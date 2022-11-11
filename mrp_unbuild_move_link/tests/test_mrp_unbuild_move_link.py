from odoo.tests import Form

from odoo.addons.mrp.tests.common import TestMrpCommon


class TestUnbuild(TestMrpCommon):
    def setUp(self):
        super(TestUnbuild, self).setUp()
        self.stock_location = self.env.ref("stock.stock_location_stock")
        self.env.ref("base.group_user").write(
            {"implied_ids": [(4, self.env.ref("stock.group_production_lot").id)]}
        )

    def test_unbuild_with_move_mrp_link(self):
        """This test creates an Unbuild order from a Manufacturing order and then
        check if the unbuild order has the id of the manufacturing order stock move.
        """
        mo, bom, p_final, p1, p2 = self.generate_mo()

        self.env["stock.quant"]._update_available_quantity(p1, self.stock_location, 100)
        self.env["stock.quant"]._update_available_quantity(p2, self.stock_location, 5)
        mo.action_assign()

        mo_form = Form(mo)
        mo_form.qty_producing = 5.0
        mo = mo_form.save()
        mo.button_mark_done()
        a = mo.button_unbuild()
        unbuild = self.env["mrp.unbuild"].create(
            {
                "product_id": a["context"]["default_product_id"],
                "mo_id": a["context"]["default_mo_id"],
                "company_id": a["context"]["default_company_id"],
                "location_id": a["context"]["default_location_id"],
                "location_dest_id": a["context"]["default_location_dest_id"],
                "product_uom_id": mo["product_uom_id"].id,
                "product_qty": 1,
            }
        )

        unbuild.action_validate()
        mo_stock_move_id = mo.move_finished_ids.id
        so = self.env["stock.move"].browse(unbuild.produce_line_ids.ids[0])
        unbuild_mo_stock_move_id = so.origin_mrp_manufacture_move_id.id

        self.assertTrue(
            unbuild_mo_stock_move_id,
            "You should have one value in origin_mrp_manufacture_move_id field"
            "in the stock move of the unbuild order",
        )
        self.assertEqual(
            mo_stock_move_id,
            unbuild_mo_stock_move_id,
            "You should have the origin manufacturing order stock move "
            "in the stock move of the unbuild order",
        )
