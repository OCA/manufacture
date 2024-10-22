# (c) 2015 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import odoo.tests as common


class TestMrpBomVersion(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestMrpBomVersion, cls).setUpClass()
        cls.parameter_model = cls.env["ir.config_parameter"].sudo()
        cls.bom_model = cls.env["mrp.bom"].with_context(test_mrp_bom_version=True)
        cls.company = cls.env.ref("base.main_company")
        vals = {
            "company_id": cls.company.id,
            "product_tmpl_id": cls.env.ref(
                "product.product_product_11_product_template"
            ).id,
            "bom_line_ids": [
                (0, 0, {"product_id": cls.env.ref("product.product_product_5").id}),
                (0, 0, {"product_id": cls.env.ref("product.product_product_6").id}),
            ],
        }
        cls.mrp_bom = cls.bom_model.create(vals)

    def test_mrp_bom(self):
        self.assertEqual(
            self.mrp_bom.state, "draft", "New BoM must be in state 'draft'"
        )
        self.assertEqual(self.mrp_bom.version, 1, "Incorrect version for new BoM")
        self.assertFalse(self.mrp_bom.active, "New BoMs must be created inactive")
        self.mrp_bom.button_activate()
        self.assertTrue(self.mrp_bom.active, "Incorrect activation, check must be True")
        self.assertEqual(
            self.mrp_bom.state, "active", "Incorrect state, it should be 'active'"
        )
        self.mrp_bom.button_historical()
        self.assertFalse(
            self.mrp_bom.active, "Check must be False, after historification"
        )
        self.assertEqual(
            self.mrp_bom.state,
            "historical",
            "Incorrect state, it should be 'historical'",
        )

    def test_mrp_bom_back2draft_default(self):
        self.mrp_bom.button_activate()
        self.mrp_bom.button_draft()
        self.assertFalse(self.mrp_bom.active, "Check must be False")

    def test_mrp_bom_back2draft_active(self):
        self.parameter_model.set_param("mrp_bom_version.active_draft", True)
        self.mrp_bom.button_activate()
        self.mrp_bom.button_draft()
        self.assertTrue(self.mrp_bom.active, "Check must be True, as set in parameters")

    def test_mrp_bom_versioning(self):
        self.mrp_bom.button_activate()
        self.mrp_bom.button_new_version()
        self.assertFalse(
            self.mrp_bom.active, "Check must be False, it must have been historified"
        )
        self.assertEqual(
            self.mrp_bom.state,
            "historical",
            "Incorrect state, it must have been historified",
        )
        new_boms = self.bom_model.with_context(active_test=False).search(
            [
                ("previous_bom_id", "=", self.mrp_bom.id),
            ]
        )
        for new_bom in new_boms:
            self.assertEqual(
                new_bom.version,
                self.mrp_bom.version + 1,
                "New BoM version must be +1 from origin BoM version",
            )
            self.assertEqual(
                new_bom.active,
                self.parameter_model.search([("key", "=", "active.draft")]).value,
                "It does not match active draft check state set in company",
            )
            self.assertEqual(
                new_bom.state, "draft", "New version must be created in 'draft' state"
            )
