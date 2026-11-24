# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.tests.common import Form, TransactionCase

from ..hooks import fill_stock_lot_bom_id, fill_stock_quant_bom_id


class TestMrpLotBom(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Models
        cls.Product = cls.env["product.product"]
        cls.Bom = cls.env["mrp.bom"]
        cls.Lot = cls.env["stock.lot"]
        cls.Quant = cls.env["stock.quant"]
        cls.Production = cls.env["mrp.production"]
        # Instances
        cls.component_a = cls._create_product(name="Component A")
        cls.component_b = cls._create_product(name="Component B")
        cls.product_serial = cls._create_product(
            name="Finished serial", tracking="serial"
        )
        cls.product_lot = cls._create_product(name="Finished lot", tracking="lot")
        cls.bom_serial_a = cls._create_bom(cls.product_serial, cls.component_a)
        cls.bom_serial_b = cls._create_bom(cls.product_serial, cls.component_b)
        cls.bom_lot_a = cls._create_bom(cls.product_lot, cls.component_a)
        cls.bom_lot_b = cls._create_bom(cls.product_lot, cls.component_b)
        # Setup
        cls.env.user.groups_id |= cls.env.ref("stock.group_production_lot")

    @classmethod
    def _create_product(cls, **kwargs):
        vals = {"name": "Product", "type": "product"}
        vals.update(kwargs)
        return cls.Product.create(vals)

    @classmethod
    def _create_bom(cls, product, component, **kwargs):
        vals = {
            "product_tmpl_id": product.product_tmpl_id.id,
            "product_qty": 1,
            "code": component.name,
            "bom_line_ids": [
                (0, 0, {"product_id": component.id, "product_qty": 1}),
            ],
        }
        vals.update(kwargs)
        return cls.Bom.create(vals)

    @classmethod
    def _create_lot(cls, product, name, **kwargs):
        vals = {
            "name": name,
            "product_id": product.id,
            "company_id": cls.env.company.id,
        }
        vals.update(kwargs)
        return cls.Lot.create(vals)

    @classmethod
    def _create_production(cls, bom, **kwargs):
        mo_form = Form(cls.Production)
        mo_form.product_id = bom.product_tmpl_id.product_variant_id
        mo_form.bom_id = bom
        mo_form.product_qty = kwargs.get("product_qty", 1)
        production = mo_form.save()
        production.action_confirm()
        return production

    @classmethod
    def _produce(cls, production, lot):
        mo_form = Form(production)
        mo_form.qty_producing = production.product_qty
        mo_form.lot_producing_id = lot
        production = mo_form.save()
        production.move_raw_ids.picked = True
        production.button_mark_done()
        return production

    def test_01_lot_bom_set_when_done(self):
        lot = self._create_lot(self.product_serial, "SN-A")
        production = self._create_production(self.bom_serial_a)
        production.lot_producing_id = lot
        self.assertFalse(lot.bom_id)
        self._produce(production, lot)
        self.assertEqual(production.state, "done")
        self.assertEqual(lot.bom_id, self.bom_serial_a)

    def test_02_quant_bom(self):
        lot_a = self._create_lot(self.product_serial, "SN-A")
        lot_b = self._create_lot(self.product_serial, "SN-B")
        self._produce(self._create_production(self.bom_serial_a), lot_a)
        self._produce(self._create_production(self.bom_serial_b), lot_b)
        domain = [
            ("product_id", "=", self.product_serial.id),
            ("location_id.usage", "=", "internal"),
        ]
        quants = self.Quant.search(domain)
        self.assertEqual(len(quants), 2)
        self.assertEqual(
            quants.filtered(lambda q: q.lot_id == lot_a).bom_id, self.bom_serial_a
        )
        self.assertEqual(
            quants.filtered(lambda q: q.lot_id == lot_b).bom_id, self.bom_serial_b
        )
        self.assertEqual(
            self.Quant.search(domain + [("bom_id", "=", self.bom_serial_b.id)]).lot_id,
            lot_b,
        )
        groups = self.Quant.read_group(domain, ["quantity:sum"], ["bom_id"])
        self.assertEqual(
            {group["bom_id"][0]: group["quantity"] for group in groups},
            {self.bom_serial_a.id: 1, self.bom_serial_b.id: 1},
        )

    def test_03_lot_produced_twice_keeps_last_bom(self):
        lot = self._create_lot(self.product_lot, "LOT-1")
        self._produce(self._create_production(self.bom_lot_a, product_qty=2), lot)
        self.assertEqual(lot.bom_id, self.bom_lot_a)
        self._produce(self._create_production(self.bom_lot_b, product_qty=3), lot)
        self.assertEqual(lot.bom_id, self.bom_lot_b)
        self.assertEqual(len(lot.production_ids), 2)

    def test_04_lot_without_production(self):
        lot = self._create_lot(self.product_serial, "SN-PURCHASED")
        self.Quant._update_available_quantity(
            self.product_serial,
            self.env.ref("stock.stock_location_stock"),
            1,
            lot_id=lot,
        )
        self.assertFalse(lot.bom_id)
        self.assertFalse(lot.quant_ids.bom_id)

    def test_05_pre_init_hook_fill(self):
        lot_a = self._create_lot(self.product_serial, "SN-A")
        lot_b = self._create_lot(self.product_serial, "SN-B")
        lot_c = self._create_lot(self.product_lot, "LOT-1")
        lot_d = self._create_lot(self.product_serial, "SN-PURCHASED")
        self._produce(self._create_production(self.bom_serial_a), lot_a)
        self._produce(self._create_production(self.bom_serial_b), lot_b)
        self._produce(self._create_production(self.bom_lot_a, product_qty=2), lot_c)
        self._produce(self._create_production(self.bom_lot_b, product_qty=3), lot_c)
        self.Quant._update_available_quantity(
            self.product_serial,
            self.env.ref("stock.stock_location_stock"),
            1,
            lot_id=lot_d,
        )
        lots = lot_a | lot_b | lot_c | lot_d
        quants = lots.quant_ids
        expected_lots = {lot: lot.bom_id for lot in lots}
        expected_quants = {quant: quant.bom_id for quant in quants}
        self.assertEqual(expected_lots[lot_c], self.bom_lot_b)
        self.env.flush_all()
        self.env.cr.execute(
            "UPDATE stock_lot SET bom_id = NULL WHERE id IN %s", (tuple(lots.ids),)
        )
        self.env.cr.execute(
            "UPDATE stock_quant SET bom_id = NULL WHERE id IN %s",
            (tuple(quants.ids),),
        )
        self.env.invalidate_all()
        self.assertFalse(lots.bom_id)
        self.assertFalse(quants.bom_id)
        fill_stock_lot_bom_id(self.env.cr)
        fill_stock_quant_bom_id(self.env.cr)
        self.env.invalidate_all()
        for lot, bom in expected_lots.items():
            self.assertEqual(lot.bom_id, bom)
        for quant, bom in expected_quants.items():
            self.assertEqual(quant.bom_id, bom)
