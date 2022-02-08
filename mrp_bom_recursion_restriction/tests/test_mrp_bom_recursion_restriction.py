# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import SavepointCase


class TestMrpBomRecursionRestriction(SavepointCase):
    def setUp(self):
        super().setUp()
        self.product_model = self.env["product.product"]
        self.bom_model = self.env["mrp.bom"]
        self.bom_line_model = self.env["mrp.bom.line"]
        self.product_a = self.product_model.create(
            {
                "name": "Product A",
                "type": "product",
            }
        )
        self.product_b = self.product_model.create(
            {
                "name": "Product B",
                "type": "product",
            }
        )
        self.product_c = self.product_model.create(
            {
                "name": "Product C",
                "type": "product",
            }
        )
        self.product_d = self.product_model.create(
            {
                "name": "Product D",
                "type": "product",
            }
        )
        self.product_e = self.product_model.create(
            {
                "name": "Product E",
                "type": "product",
            }
        )
        self.product_f = self.product_model.create(
            {
                "name": "Product F",
                "type": "product",
            }
        )
        self.bom_a = self.bom_model.create(
            {
                "product_tmpl_id": self.product_a.product_tmpl_id.id,
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_b.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_c.id,
                        },
                    ),
                ],
            }
        )
        self.bom_b = self.bom_model.create(
            {
                "product_tmpl_id": self.product_b.product_tmpl_id.id,
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_c.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_d.id,
                        },
                    ),
                ],
            }
        )
        self.bom_c = self.bom_model.create(
            {
                "product_tmpl_id": self.product_c.product_tmpl_id.id,
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_d.id,
                        },
                    )
                ],
            }
        )
        self.bom_d = self.bom_model.create(
            {
                "product_tmpl_id": self.product_d.product_tmpl_id.id,
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_a.id,
                        },
                    )
                ],
            }
        )

    def _check_has_recursion(self):
        self.bom_a and self.assertTrue(self.bom_a.has_recursion)
        self.bom_b and self.assertTrue(self.bom_b.has_recursion)
        self.bom_c and self.assertTrue(self.bom_c.has_recursion)
        self.bom_d and self.assertTrue(self.bom_d.has_recursion)

    def _check_not_has_recursion(self):
        self.bom_a and self.assertFalse(self.bom_a.has_recursion)
        self.bom_b and self.assertFalse(self.bom_b.has_recursion)
        self.bom_c and self.assertFalse(self.bom_c.has_recursion)
        self.bom_d and self.assertFalse(self.bom_d.has_recursion)

    def test_recursion_method(self):
        # Start with recursion case
        self._check_has_recursion()

        # fix recursion on last bom line
        self.bom_d.bom_line_ids.filtered(
            lambda x: x.product_id.id == self.product_a.id
        ).write({"product_id": self.product_e.id})
        self._check_not_has_recursion()

        # recursive again
        self.bom_d.bom_line_ids.write({"product_id": self.product_a.id})
        self._check_has_recursion()

        # fix recursion break a link in the chain
        self.bom_a.bom_line_ids.write({"product_id": self.product_f.id})
        self.bom_b.bom_line_ids.write({"product_id": self.product_f.id})
        self._check_not_has_recursion()

        # recursive again
        self.bom_a.bom_line_ids.write({"product_id": self.product_b.id})
        self.bom_b.bom_line_ids.write({"product_id": self.product_c.id})
        self._check_has_recursion()

        # Change bom product template break recursion
        self.bom_a.write(
            {
                "product_tmpl_id": self.product_f.product_tmpl_id.id,
            }
        )
        self._check_not_has_recursion()

        # Recursion Again
        self.bom_a.write(
            {
                "product_tmpl_id": self.product_a.product_tmpl_id.id,
            }
        )
        self._check_has_recursion()

        # fix recursion deleting bom line
        self.bom_d.bom_line_ids.unlink()
        self._check_not_has_recursion()

        # Recursion Again
        self.bom_line_model.create(
            {
                "bom_id": self.bom_d.id,
                "product_id": self.product_a.id,
            }
        )
        self._check_has_recursion()

        # fix recursion deleting bom
        self.bom_d.unlink()
        # CHECK ME: It's necessary?
        self.bom_d = self.bom_model.browse()
        self._check_not_has_recursion()
