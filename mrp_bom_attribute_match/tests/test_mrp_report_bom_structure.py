from odoo import Command

from .common import TestMrpBomAttributeMatchBase


class TestMrpReportBomStructure(TestMrpBomAttributeMatchBase):
    def test_get_report_data_drops_dynamic_component_without_variant(self):
        # Drop the Cyan value from the plastic template so the Cyan sword
        # variant has no resolvable plastic variant. This forces the override
        # to hit the `to_ignore_line_ids.append` + `Command.unlink` branch.
        cyan_value = self.plastic_attrs.value_ids.filtered(lambda v: v.name == "Cyan")
        self.plastic_attrs.value_ids = [Command.unlink(cyan_value.id)]
        sword_cyan = self.product_sword.product_variant_ids.filtered(
            lambda p: "Cyan" in p.display_name
        )
        BomStructureReport = self.env["report.mrp.report_bom_structure"]
        res = BomStructureReport._get_report_data(
            self.bom_id.id, searchVariant=sword_cyan.id
        )
        # The dynamic plastic line was unlinked from the virtual BoM —
        # only the static paper component remains.
        component_product_ids = [c["product_id"] for c in res["lines"]["components"]]
        products = self.env["product.product"].browse(component_product_ids)
        self.assertNotIn(self.product_plastic, products.product_tmpl_id)
        self.assertIn(self.product_9, products)

    def test_get_report_data_resolves_dynamic_component_and_serialises_ids(self):
        # Happy path: Cyan sword resolves the dynamic plastic line to the
        # Cyan plastic variant, and every component's `product_id` ends up
        # as a plain int (NewId origin replaced).
        sword_cyan = self.product_sword.product_variant_ids.filtered(
            lambda p: "Cyan" in p.display_name
        )
        plastic_cyan = self.product_plastic.product_variant_ids.filtered(
            lambda p: "Cyan" in p.display_name
        )
        BomStructureReport = self.env["report.mrp.report_bom_structure"]
        res = BomStructureReport._get_report_data(
            self.bom_id.id, searchVariant=sword_cyan.id
        )
        components = res["lines"]["components"]
        for component in components:
            self.assertIsInstance(component["product_id"], int)
        component_ids = [c["product_id"] for c in components]
        self.assertIn(plastic_cyan.id, component_ids)
        self.assertIn(self.product_9.id, component_ids)

    def test_get_report_data_passes_through_without_dynamic_lines(self):
        # BoM without `component_template_id` lines must skip the override
        # branch entirely and return parent-class data unchanged.
        BomStructureReport = self.env["report.mrp.report_bom_structure"]
        res = BomStructureReport._get_report_data(self.fin_bom_id.id)
        self.assertIn("lines", res)
        self.assertEqual(
            res["lines"]["product"],
            self.product_fin.product_variant_ids[0],
        )
        self.assertEqual(
            res["lines"]["components"][0]["product_id"],
            self.product_plastic.product_variant_ids[0].id,
        )
