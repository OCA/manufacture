from odoo.tests import Form

from odoo.addons.mrp.tests.common import TestMrpCommon


class TestUnbuild(TestMrpCommon):
    def setUp(self):
        super(TestUnbuild, self).setUp()
        self.stock_location = self.env.ref("stock.stock_location_stock")
        self.env.ref("base.group_user").write(
            {"implied_ids": [(4, self.env.ref("stock.group_production_lot").id)]}
        )

    def test_unbuild_with_valuation_layer(self):
        """This test creates an Unbuild order from a Manufacturing order and then check if the
        valuation button links to the valuation layer of the order.
        """
        mo, bom, p_final, p1, p2 = self.generate_mo()

        self.env["stock.quant"]._update_available_quantity(p1, self.stock_location, 100)
        self.env["stock.quant"]._update_available_quantity(p2, self.stock_location, 5)
        mo.action_assign()

        mo_form = Form(mo)
        mo_form.qty_producing = 5.0
        mo = mo_form.save()
        mo.button_mark_done()
        layers_before_unbuild = (
            self.env["stock.move"].search([]).stock_valuation_layer_ids.ids
        )

        x = Form(self.env["mrp.unbuild"])
        x.product_id = p_final
        x.bom_id = bom
        x.product_qty = 5
        unbuild = x.save()
        unbuild.action_unbuild()
        layers_after_unbuild = (
            self.env["stock.move"].search([]).stock_valuation_layer_ids.ids
        )

        result = unbuild.action_view_stock_valuation_layers()
        domain = result["domain"]
        unbuild_valuation_layers = domain[0][2]
        difference_layers = list(set(layers_after_unbuild) - set(layers_before_unbuild))

        self.assertTrue(
            difference_layers, "There should be new layers after doing the unbuild"
        )
        self.assertEqual(
            result["res_model"],
            "stock.valuation.layer",
            "You should access to the model stock.valuation.layer",
        )
        self.assertEqual(
            difference_layers,
            unbuild_valuation_layers,
            "You should have as domain the ids of the stock valuation belonging "
            "to the ids of the stock moves of produce_line and consume_line",
        )
