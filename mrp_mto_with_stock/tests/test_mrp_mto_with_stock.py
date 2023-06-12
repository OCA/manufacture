# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestMrpMtoWithStock(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestMrpMtoWithStock, self).setUp(*args, **kwargs)
        self.production_model = self.env["mrp.production"]
        self.procurement_model = self.env["procurement.group"]
        self.bom_model = self.env["mrp.bom"]
        self.stock_location_stock = self.env.ref("stock.stock_location_stock")
        self.manufacture_route = self.env.ref("mrp.route_warehouse0_manufacture")
        self.uom_unit = self.env.ref("uom.product_uom_unit")
        self.warehouse = self.env.ref("stock.warehouse0")

        self.top_product = self.env.ref(
            "mrp_mto_with_stock.product_product_manufacture_1"
        )
        self.subproduct1 = self.env.ref(
            "mrp_mto_with_stock.product_product_manufacture_1_1"
        )
        self.subproduct2 = self.env.ref(
            "mrp_mto_with_stock.product_product_manufacture_1_2"
        )
        self.subproduct_1_1 = self.env.ref(
            "mrp_mto_with_stock.product_product_manufacture_1_1_1"
        )

        self.main_bom = self.env.ref("mrp_mto_with_stock.mrp_bom_manuf_1")

    def _update_product_qty(self, product, quantity):
        """Update Product quantity."""
        product_qty = self.env["stock.change.product.qty"].create(
            {
                "product_tmpl_id": product.product_tmpl_id.id,
                "product_id": product.id,
                "new_quantity": quantity,
            }
        )
        product_qty.change_product_qty()

    def test_manufacture_with_forecast_stock(self):
        """
        Test Manufacture mto with stock based on forecast quantity
        and no link between sub assemblies MO's and Main MO raw material
        """

        self.warehouse.mrp_mto_mts_forecast_qty = True

        self._update_product_qty(self.subproduct1, 2)
        self._update_product_qty(self.subproduct2, 4)

        # Create MO and check it create sub assemblie MO.
        self.production = Form(self.env["mrp.production"])
        self.production.product_id = self.top_product
        self.production.product_uom_id = self.uom_unit
        self.production.bom_id = self.main_bom
        self.production.product_qty = 1.0
        self.production = self.production.save()

        self.assertEqual(self.subproduct1.virtual_available, 2)
        self.production_sub1 = self.production_model.search(
            [("id", "=", self.production.id)]
        )
        self.assertEqual(self.production_sub1.state, "draft")
        self.assertEqual(len(self.production_sub1), 1)
        self.assertEqual(self.production_sub1.product_qty, 1)
        self._update_product_qty(self.subproduct1, 7)

        # Create second MO and check it does not create procurement
        self.production2 = Form(self.env["mrp.production"])
        self.production2.product_id = self.top_product
        self.production2.product_uom_id = self.uom_unit
        self.production2.bom_id = self.main_bom
        self.production2.product_qty = 1.0
        self.production2 = self.production2.save()

        p = self.production_model.search([("origin", "ilike", self.production2.name)])
        self.assertEqual(len(p), 0)
        self.production2.do_unreserve()
        self.assertEqual(self.subproduct1.virtual_available, 7)

    def test_manufacture_with_reservable_stock(self):
        """
        Test Manufacture mto with stock based on reservable stock
        and there is a link between sub assemblies MO's and Main MO raw
        material
        """

        self._update_product_qty(self.subproduct1, 2)
        self._update_product_qty(self.subproduct2, 4)
        self._update_product_qty(self.subproduct_1_1, 50)

        self.main_bom.write(
            {
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.subproduct_1_1.id,
                            "product_qty": 1.0,
                            "product_uom_id": self.subproduct_1_1.uom_id.id,
                        },
                    )
                ]
            }
        )

        self.production = Form(self.env["mrp.production"])
        self.production.product_id = self.top_product
        self.production.product_uom_id = self.uom_unit
        self.production.bom_id = self.main_bom
        self.production.product_qty = 3.0
        self.production = self.production.save()

        self.assertEqual(len(self.production.move_raw_ids), 3)

        self.assertEqual(self.production.product_qty, 3)

        self.production.action_assign()
        self.production.button_mark_done()
        self.assertEqual(self.subproduct1.qty_available, 2)
