from odoo.tests.common import TransactionCase


class TestBomConfigurable(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product_obj = cls.env["product.product"]

        cls.bom_obj = cls.env["mrp.bom"]
        cls.bom_line_obj = cls.env["mrp.bom.line"]

        cls.input_config_obj = cls.env["input.config"]
        cls.input_config_line_obj = cls.env["input.line"]

        # Create product
        cls.product_1 = cls.product_obj.create({"name": "TEST 01", "type": "product"})
        cls.component_1 = cls.product_obj.create(
            {"name": "Product True", "type": "product"}
        )
        cls.component_2 = cls.product_obj.create(
            {"name": "Product False", "type": "product"}
        )
        cls.component_3 = cls.product_obj.create(
            {"name": "Product None", "type": "product"}
        )

        # Create bom
        cls.bom = cls.bom_obj.create(
            {"product_tmpl_id": cls.product_1.product_tmpl_id.id}
        )
        cls.line_1 = cls.bom_line_obj.create(
            {
                "product_id": cls.component_2.id,
                "bom_id": cls.bom.id,
                "product_qty": 2.0,
                "domain": "['OR', ('test_config', '==', True), ('test_config', '==', True)]",
            }
        )
        cls.line_2 = cls.bom_line_obj.create(
            {
                "product_id": cls.component_3.id,
                "bom_id": cls.bom.id,
                "product_qty": 5.0,
                "domain": "[('test_config', '==', False)]",
            }
        )
        cls.line_2 = cls.bom_line_obj.create(
            {
                "product_id": cls.component_2.id,
                "bom_id": cls.bom.id,
                "product_qty": 5.0,
            }
        )
        cls.child_bom = cls.bom_obj.create(
            {"product_tmpl_id": cls.component_3.product_tmpl_id.id}
        )
        cls.line_3 = cls.bom_line_obj.create(
            {
                "product_id": cls.component_2.id,
                "bom_id": cls.child_bom.id,
                "product_qty": 5.0,
            }
        )
        cls.line_4 = cls.bom_line_obj.create(
            {
                "product_id": cls.component_2.id,
                "bom_id": cls.child_bom.id,
                "product_qty": 5.0,
            }
        )

        # Create config
        cls.input_config = cls.input_config_obj.create(
            {
                "name": "Test config",
            }
        )
        cls.input_line = cls.input_config_line_obj.create(
            {
                "name": "test_1",
                "bom_id": cls.bom.id,
                "config_id": cls.input_config.id,
                "test_config": True,
            }
        )
        cls.input_line_2 = cls.input_config_line_obj.create(
            {
                "name": "test_1",
                "bom_id": cls.bom.id,
                "config_id": cls.input_config.id,
                "test_config": False,
            }
        )

    def test_01_configurable_bom(self):
        self.input_line.ui_configure()
        self.input_line_2.ui_configure()
        boms = self.env["mrp.bom"].search([("configuration_type", "=", "configured")])
        self.assertEqual(len(boms), 2)
        self.assertEqual(len(boms[0].bom_line_ids), 2)
        self.assertEqual(len(boms[1].bom_line_ids), 3)

    def test_01_configurable_bom_report(self):
        report_values = self.env[
            "mrp_bom_configurable.report.mrp.report_bom_structure"
        ]._get_report_data(self.bom.id)
        self.assertIn("domain", report_values["lines"]["components"][0])
