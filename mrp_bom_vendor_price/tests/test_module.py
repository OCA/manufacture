# from odoo.exceptions import UserError
from odoo.tests import common, Form


class Test(common.TransactionCase):
    def _create_product(self, name, price):
        return self.env["product.product"].create(
            {
                "name": name,
                "type": "product",
                "standard_price": price,
                "default_code": "**",
                "company_id": 1,
            }
        )

    def _create_sup_info(self, name, price):
        product = getattr(self, name)
        self.env["product.supplierinfo"].create(
            {
                "name": self.env.ref("base.res_partner_3").id,
                "price": price,
                "product_tmpl_id": product.product_tmpl_id.id,
            }
        )

    def setUp(self):
        super().setUp()

        # # Mainly copied from mrp_bom_cost
        # Products.
        self.dining_table = self._create_product("Dining Table", 1000)
        self.table_head = self._create_product("Table Head", 300)
        self.screw = self._create_product("Screw", 10)
        self.leg = self._create_product("Leg", 25)
        self.glass = self._create_product("Glass", 100)

        # Unit of Measure.
        self.unit = self.env.ref("uom.product_uom_unit")
        self.dozen = self.env.ref("uom.product_uom_dozen")

        # Bills Of Materials.
        # -------------------------------------------------------------------------------
        # Cost of BoM (Dining Table 1 Unit)
        # Component Cost =  Table Head   1 Unit * 300 = 300 (468.75 from it's components)
        #                   Screw        5 Unit *  10 =  50
        #                   Leg          4 Unit *  25 = 100
        #                   Glass        1 Unit * 100 = 100
        # Total = 550 [718.75 if components of Table Head considered] (for 1 Unit)
        # -------------------------------------------------------------------------------

        bom_form = Form(self.env["mrp.bom"])
        bom_form.product_id = self.dining_table
        bom_form.product_tmpl_id = self.dining_table.product_tmpl_id
        bom_form.product_qty = 1.0
        bom_form.product_uom_id = self.unit
        bom_form.type = "normal"
        with bom_form.bom_line_ids.new() as line:
            line.product_id = self.table_head
            line.product_qty = 1
        with bom_form.bom_line_ids.new() as line:
            line.product_id = self.screw
            line.product_qty = 5
        with bom_form.bom_line_ids.new() as line:
            line.product_id = self.leg
            line.product_qty = 4
        with bom_form.bom_line_ids.new() as line:
            line.product_id = self.glass
            line.product_qty = 1
        bom_form.save()

        self._create_sup_info("screw", 17)
        self.screw.set_vendor_price()

    def test_vendor_price_method(self):
        self.assertEqual(self.screw.cost_vendor_price, 17)

    def test_on_final_product(self):
        self.dining_table.action_bom_vendor_price()
        self.assertEqual(self.dining_table.cost_vendor_price, 585)
