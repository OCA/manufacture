from odoo import Command

from odoo.addons.base.tests.common import BaseCommon


class TestMrpBomProductAllergen(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.main_product = cls.env.ref(
            "product.product_product_3_product_template"
        )  # Desk Combination
        cls.comp_1 = cls.env.ref("product.product_product_12")  # Office Chair Black
        cls.comp_2 = cls.env.ref("product.product_product_13")  # Corner Desk Left Sit
        cls.comp_3 = cls.env.ref("product.product_product_12")  # Drawer Black
        cls.comp_1.allergen_ids = [
            Command.link(cls.env.ref("product_allergen.allergen_gluten").id)
        ]
        cls.comp_2.allergen_ids = [
            Command.link(cls.env.ref("product_allergen.allergen_soybeans").id)
        ]
        cls.comp_3.allergen_ids = [
            Command.link(cls.env.ref("product_allergen.allergen_sesame").id)
        ]
        cls.main_recurs_product = cls.env.ref(
            "mrp.product_product_computer_desk_head"
        )  # Table Top
        cls.comp_4 = cls.env.ref("mrp.product_product_wood_panel")  # Wood Panel
        cls.comp_5_1 = cls.env.ref("mrp.product_product_wood_ply")  # Ply Layer
        cls.comp_5_2 = cls.env.ref("mrp.product_product_wood_wear")  # Wear Layer
        cls.comp_5_1.allergen_ids = [
            Command.link(cls.env.ref("product_allergen.allergen_crustaceans").id)
        ]
        cls.comp_5_2.allergen_ids = [
            Command.link(cls.env.ref("product_allergen.allergen_fish").id)
        ]

    def test_product_button_bom_allergens(self):
        """Check that allergen_ids is correctly assign based on BoM."""
        self.main_product.button_bom_allergens()
        self.assertEqual(
            set(self.main_product.allergen_ids.ids),
            set(
                [
                    self.env.ref("product_allergen.allergen_gluten").id,
                    self.env.ref("product_allergen.allergen_soybeans").id,
                    self.env.ref("product_allergen.allergen_sesame").id,
                ]
            ),
        )

    def test_product_button_bom_allergens_recurs(self):
        """Check that allergen_ids is correctly assign based on recursive BoM."""
        self.comp_4.button_bom_allergens()
        self.assertEqual(
            set(self.comp_4.allergen_ids.ids),
            set(
                [
                    self.env.ref("product_allergen.allergen_crustaceans").id,
                    self.env.ref("product_allergen.allergen_fish").id,
                ]
            ),
        )
        self.main_recurs_product.button_bom_allergens()
        self.assertEqual(
            set(self.main_recurs_product.allergen_ids.ids),
            set(
                [
                    self.env.ref("product_allergen.allergen_crustaceans").id,
                    self.env.ref("product_allergen.allergen_fish").id,
                ]
            ),
        )
        self.bom = self.env.ref("mrp.mrp_bom_table_top")
        self.warehouse = self.env.ref("stock.warehouse0")
        bom_data = self.env["report.mrp.report_bom_structure"]._get_bom_data(
            self.bom, self.warehouse, self.bom.product_id, ignore_stock=True
        )
        self.assertEqual(
            len(bom_data["allergen_imgs"]),
            2,
        )
