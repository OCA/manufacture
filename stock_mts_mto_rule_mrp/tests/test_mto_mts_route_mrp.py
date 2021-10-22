# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestMtoMtsRouteMRP(TransactionCase):

    def setUp(self):
        super().setUp()
        wh = self.env.ref("stock.warehouse0")
        self.wh = wh
        wh.manufacture_steps = "pbm"  # 2 step manufacturing
        route = self.env["stock.location.route"].search(
            [("warehouse_ids", "=", wh.id),
             ("name", "like", "% Pick components and then manufacture")]
        )
        mto_rule = route.rule_ids.filtered(
            lambda r: r.location_id.usage == "production"
        )
        mto_rule.name = "%s MTO" % mto_rule.name
        mts_rule = mto_rule.copy({"name": mto_rule.name.replace("MTO", "MTS"),
                                  "procure_method": "make_to_stock"})
        # mts_mto_rule
        self.env["stock.rule"].create(
            {
                "route_id": route.id,
                "name": "choose MTS MTO",
                "action": "split_procurement",
                "mts_rule_id": mts_rule.id,
                "mto_rule_id": mto_rule.id,
                "picking_type_id": mts_rule.picking_type_id.id,
                "location_id": mts_rule.location_id.id,
                "location_src_id": mts_rule.location_src_id.id,
                "warehouse_id": wh.id
            }
        )
        self.stock_location = wh.lot_stock_id
        self.preprod_location = wh.pbm_loc_id
        self.finished_product = self.env["product.product"].create(
            {
                "name": "finished_product",
                "type": "product",
                "sale_line_warn": "no-message",
            }
        )
        self.component_product = self.env["product.product"].create(
            {
                "name": "component",
                "type": "product",
                "sale_line_warn": "no-message",
            }
        )
        self.bom = self.env["mrp.bom"].create(
            {
                "product_id": self.finished_product.id,
                "product_tmpl_id": self.finished_product.product_tmpl_id.id,
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.component_product.id,
                            "product_qty": 2,
                            "product_uom_id": self.component_product.uom_id.id
                        }
                    )
                ]
            }
        )

    def _create_mo(self):
        manufacture = self.wh.manu_type_id
        return self.env["mrp.production"].create(
            {
                "product_id": self.finished_product.id,
                "bom_id": self.bom.id,
                "product_qty": 1,
                "product_uom_id": self.finished_product.uom_id.id,
                "picking_type_id": self.wh.manu_type_id.id,
                "location_src_id": manufacture.default_location_src_id.id,
                "location_dest_id": manufacture.default_location_dest_id.id,
            }
        )

    def test_stock_in_stock(self):
        """quantity in WH/Stock = 2 -> take 2 in stock to preprod"""
        self.env["stock.quant"]._update_available_quantity(
            self.component_product, self.stock_location, 2
        )
        mo = self._create_mo()
        self.assertEqual(mo.move_raw_ids.procure_method, "make_to_order")

    def test_stock_in_preprod(self):
        """quantity in WH/Preprod = 2 -> take 2 in preprod"""
        self.env["stock.quant"]._update_available_quantity(
            self.component_product, self.preprod_location, 2
        )
        mo = self._create_mo()
        self.assertEqual(mo.move_raw_ids.procure_method, "make_to_stock")

    def test_stock_in_preprod_and_in_stock(self):
        """quantity in WH/PreProd = 1 -> take 1 in preprod,
        and fetch the rest from stock"""
        self.env["stock.quant"]._update_available_quantity(
            self.component_product, self.preprod_location, 1
        )
        mo = self._create_mo()
        self.assertEqual(
            len(
                mo.move_raw_ids.filtered(
                    lambda r: r.procure_method == "make_to_stock"
                )
            ),
            1
        )
        self.assertEqual(
            len(
                mo.move_raw_ids.filtered(
                    lambda r: r.procure_method == "make_to_order"
                )
            ),
            1
        )
