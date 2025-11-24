# (c) 2015 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import Command

from odoo.addons.base.tests.common import BaseCommon


class TestMrpBomVersion(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.parameter_model = cls.env["ir.config_parameter"].sudo()
        cls.bom_model = cls.env["mrp.bom"].with_context(test_mrp_bom_version=True)
        cls.company = cls.env.ref("base.main_company")
        vals = {
            "company_id": cls.company.id,
            "product_tmpl_id": cls.env.ref(
                "product.product_product_11_product_template"
            ).id,
            "bom_line_ids": [
                Command.create(
                    {"product_id": cls.env.ref("product.product_product_5").id}
                ),
                Command.create(
                    {"product_id": cls.env.ref("product.product_product_6").id}
                ),
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

    def test_historical_bom_still_used_in_picking(self):
        self.mrp_bom.button_activate()
        kit_product = self.mrp_bom.product_tmpl_id.product_variant_id

        picking = self.env["stock.picking"].create(
            {
                "partner_id": self.env.ref("base.res_partner_1").id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
            }
        )
        bom_line_5 = self.mrp_bom.bom_line_ids.filtered(
            lambda l: l.product_id == self.env.ref("product.product_product_5")
        )
        bom_line_6 = self.mrp_bom.bom_line_ids.filtered(
            lambda l: l.product_id == self.env.ref("product.product_product_6")
        )

        self.env["stock.move"].create(
            {
                "name": "Kit Move – compo 5",
                "product_id": self.env.ref("product.product_product_5").id,
                "product_uom_qty": 1,
                "product_uom": kit_product.uom_id.id,
                "picking_id": picking.id,
                "location_id": picking.location_id.id,
                "location_dest_id": picking.location_dest_id.id,
                "bom_line_id": bom_line_5.id,
            }
        )
        self.env["stock.move"].create(
            {
                "name": "Kit Move – compo 6",
                "product_id": self.env.ref("product.product_product_6").id,
                "product_uom_qty": 1,
                "product_uom": kit_product.uom_id.id,
                "picking_id": picking.id,
                "location_id": picking.location_id.id,
                "location_dest_id": picking.location_dest_id.id,
                "bom_line_id": bom_line_6.id,
            }
        )

        picking.action_assign()
        picking.button_validate()

        filters = {
            "incoming_moves": lambda m: m.id in picking.move_ids.ids,
            "outgoing_moves": lambda m: m.id not in picking.move_ids.ids,
        }

        qty = picking.move_ids._compute_kit_quantities(
            product_id=kit_product,
            kit_qty=1,
            kit_bom=self.mrp_bom,
            filters=filters,
        )
        self.assertEqual(qty, 1.0)

        self.mrp_bom.button_new_version()
        new_bom = self.bom_model.with_context(active_test=False).search(
            [
                ("previous_bom_id", "=", self.mrp_bom.id),
            ],
            limit=1,
        )
        qty2 = picking.move_ids._compute_kit_quantities(
            product_id=kit_product,
            kit_qty=1,
            kit_bom=new_bom,
            filters=filters,
        )
        self.assertEqual(qty2, 1.0)
