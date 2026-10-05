# Copyright 2026 Open Source Integrators
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import Command
from odoo.tests import Form, TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestMrpWorkorderTimeFormula(TransactionCase):
    """
    Tests for the time_fixed / time_cadence duration formula.

    All tests use a simple workcenter (capacity=1, efficiency=100%,
    no start/stop) so the expected duration formula reduces to:

        duration = cycle_number * time_cycle_manual   (standard)
                 + time_fixed                         (fixed setup)
                 + cycle_number * (1 / time_cadence)  (cadence)

    with cycle_number = ceil(qty / capacity) = qty.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.workcenter = cls.env["mrp.workcenter"].create(
            {
                "name": "Test Workcenter",
                "default_capacity": 1,
                "time_start": 0,
                "time_stop": 0,
                "time_efficiency": 100,
            }
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _make_product(self, name="Finished Product"):
        return self.env["product.product"].create({"name": name, "type": "product"})

    def _make_bom_with_operation(
        self,
        product,
        time_cycle_manual=0.0,
        time_fixed=0.0,
        time_cadence=0.0,
    ):
        return self.env["mrp.bom"].create(
            {
                "product_tmpl_id": product.product_tmpl_id.id,
                "product_id": product.id,
                "product_qty": 1.0,
                "product_uom_id": self.uom_unit.id,
                "type": "normal",
                "operation_ids": [
                    Command.create(
                        {
                            "name": "Test Operation",
                            "workcenter_id": self.workcenter.id,
                            "time_cycle_manual": time_cycle_manual,
                            "time_fixed": time_fixed,
                            "time_cadence": time_cadence,
                        }
                    )
                ],
            }
        )

    def _make_production_order(self, product, bom, qty):
        mo_form = Form(self.env["mrp.production"])
        mo_form.product_id = product
        mo_form.bom_id = bom
        mo_form.product_qty = qty
        return mo_form.save()

    def _get_workorder_duration(self, production):
        self.assertEqual(len(production.workorder_ids), 1)
        return production.workorder_ids[0].duration_expected

    # ------------------------------------------------------------------
    # Tests
    # ------------------------------------------------------------------

    def test_time_fixed_only(self):
        """Fixed duration adds a flat amount regardless of qty."""
        product = self._make_product()
        bom = self._make_bom_with_operation(product, time_fixed=10.0)

        mo_qty1 = self._make_production_order(product, bom, qty=1)
        mo_qty5 = self._make_production_order(product, bom, qty=5)

        self.assertAlmostEqual(self._get_workorder_duration(mo_qty1), 10.0)
        self.assertAlmostEqual(self._get_workorder_duration(mo_qty5), 10.0)

    def test_time_cadence_only(self):
        """Cadence time scales linearly with quantity."""
        product = self._make_product()
        bom = self._make_bom_with_operation(product, time_cadence=5.0)

        mo_qty10 = self._make_production_order(product, bom, qty=10)
        mo_qty20 = self._make_production_order(product, bom, qty=20)

        # 10 units at 5 units/min = 2 min ; 20 units = 4 min
        self.assertAlmostEqual(self._get_workorder_duration(mo_qty10), 2.0)
        self.assertAlmostEqual(self._get_workorder_duration(mo_qty20), 4.0)

    def test_time_cycle_manual_and_time_fixed_and_time_cadence(self):
        """All three contributions are summed correctly."""
        product = self._make_product()
        bom = self._make_bom_with_operation(
            product,
            time_cycle_manual=2.0,
            time_fixed=10.0,
            time_cadence=5.0,
        )
        mo = self._make_production_order(product, bom, qty=20)

        # cycle_number = 20, standard = 20*2 = 40, fixed = 10, cadence = 20/5 = 4
        expected = 40.0 + 10.0 + 4.0
        self.assertAlmostEqual(self._get_workorder_duration(mo), expected)

    def test_no_extra_fields_unchanged(self):
        """When both extra fields are zero, duration equals the standard formula."""
        product = self._make_product()
        bom = self._make_bom_with_operation(product, time_cycle_manual=3.0)

        mo = self._make_production_order(product, bom, qty=10)

        # Standard only: 10 * 3 = 30 min
        self.assertAlmostEqual(self._get_workorder_duration(mo), 30.0)

    def test_time_cadence_zero_does_not_contribute(self):
        """A cadence of 0 is ignored (no division by zero)."""
        product = self._make_product()
        bom = self._make_bom_with_operation(
            product, time_cycle_manual=2.0, time_cadence=0.0
        )
        mo = self._make_production_order(product, bom, qty=5)

        self.assertAlmostEqual(self._get_workorder_duration(mo), 10.0)
