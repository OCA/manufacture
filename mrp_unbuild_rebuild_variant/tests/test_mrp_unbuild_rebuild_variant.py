# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import exceptions
from odoo.tests import SavepointCase


class TestMrpUnbuildRebuildVariant(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        ref = cls.env.ref

        # Ref products
        cls.product_amplifier_phono_tuner = ref(
            "mrp_unbuild_rebuild_variant."
            "product_product_amplifier_with_phono_with_tuner"
        )
        cls.product_amplifier_tuner = ref(
            "mrp_unbuild_rebuild_variant."
            "product_product_amplifier_without_phono_with_tuner"
        )
        cls.product_amplifier_phono = ref(
            "mrp_unbuild_rebuild_variant."
            "product_product_amplifier_with_phono_without_tuner"
        )
        cls.product_amp_case = ref(
            "mrp_unbuild_rebuild_variant.product_product_amplifier_case"
        )
        cls.product_amp_preamp = ref(
            "mrp_unbuild_rebuild_variant.product_product_amplifier_preamp"
        )
        cls.product_amp_power_amp = ref(
            "mrp_unbuild_rebuild_variant.product_product_amplifier_power_amp"
        )
        cls.product_amp_phono = ref(
            "mrp_unbuild_rebuild_variant.product_product_amplifier_phono"
        )
        cls.product_amp_tuner = ref(
            "mrp_unbuild_rebuild_variant.product_product_amplifier_tuner"
        )

        # Ref bom, locations
        cls.amplifier_bom = ref("mrp_unbuild_rebuild_variant.mrp_bom_amplifier")
        cls.stock_location = ref("stock.stock_location_stock")

        # Init inventory
        inventory_matrix = {
            cls.product_amp_case: ["000123", ],
            cls.product_amp_preamp: ["100456", ],
            cls.product_amp_power_amp: ["200789", ],
            cls.product_amp_phono: ["300321", ],
            cls.product_amp_tuner: ["400654", ],
        }
        cls._set_inventory(inventory_matrix)

        # Create original manufacturing orders
        cls.amplifier_phono_tuner_50001_mo = cls._create_manufacturing_order(
            cls.product_amplifier_phono_tuner, 1.0, cls.amplifier_bom
        )
        cls.amplifier_phono_tuner_50001_mo.action_assign()
        # Ensure serials are mapped correctly (shouldn't be necessary if no
        #  other addons changes assignation rules, but let's be safe)
        inventory_matrix = {
            cls.product_amp_case: "000123",
            cls.product_amp_preamp: "100456",
            cls.product_amp_power_amp: "200789",
            cls.product_amp_phono: "300321",
            cls.product_amp_tuner: "400654",
        }
        for move in cls.amplifier_phono_tuner_50001_mo.move_raw_ids:
            raw_product = move.product_id
            move_line = move.move_line_ids
            serial_to_use = inventory_matrix.get(raw_product)
            if move_line.lot_id.name != serial_to_use:
                raw_lot = cls.env["stock.production.lot"].search(
                    [
                        ("product_id", '=', raw_product.id),
                        ("name", "=", serial_to_use)
                    ]
                )
                move_line.lot_id = raw_lot.id
        produce_wiz = (
            cls.env["mrp.product.produce"]
            .with_context(active_id=cls.amplifier_phono_tuner_50001_mo.id)
            .create({})
        )
        cls.lot_50001 = cls._create_lot_number(
            cls.product_amplifier_phono_tuner, "50001"
        )
        produce_wiz.lot_id = cls.lot_50001
        produce_wiz.do_produce()

    @classmethod
    def _create_lot_number(cls, product, lot_number):
        return cls.env["stock.production.lot"].create(
            {"product_id": product.id, "name": lot_number}
        )

    @classmethod
    def _set_inventory(cls, inventory_matrix):
        for product, serials in inventory_matrix.items():
            for number in serials:
                lot = cls._create_lot_number(product, number)
                cls.env["stock.quant"]._update_available_quantity(
                    product, cls.stock_location, 1.0, lot_id=lot
                )

    @classmethod
    def _create_manufacturing_order(cls, product, product_qty, bom):
        return cls.env["mrp.production"].create(
            {
                "product_id": product.id,
                "product_qty": product_qty,
                "product_uom_id": product.uom_id.id,
                "bom_id": bom.id,
            }
        )

    def test_unbuild_rebuild(self):
        rebuild_order = self.env["mrp.unbuild.rebuild.variant"].create(
            {
                "unbuild_bom_id": self.amplifier_bom.id,
                "unbuild_product_id": self.product_amplifier_phono_tuner.id,
                "unbuild_lot_id": self.lot_50001.id,
                "quantity": 1.0,
                "rebuild_bom_id": self.amplifier_bom.id,
                "rebuild_product_id": self.product_amplifier_tuner.id,
            }
        )
        # No tuner amplifier in stock
        qty_amplifier_tuner = self.env["stock.quant"]._get_available_quantity(
            self.product_amplifier_tuner, self.stock_location
        )
        self.assertAlmostEqual(
            qty_amplifier_tuner, 0.0, msg="There should be no tuner amplifier in stock"
        )
        rebuild_order.process()
        # Phono tuner amplifier should have been consumed
        qty_amplifier_phono_tuner = self.env["stock.quant"]._get_available_quantity(
            self.product_amplifier_phono_tuner, self.stock_location
        )
        self.assertAlmostEqual(
            qty_amplifier_phono_tuner,
            0.0,
            msg="There should be no phono tuner amplifier in stock",
        )
        # Phono amplifier should have been created
        qty_amplifier_tuner = self.env["stock.quant"]._get_available_quantity(
            self.product_amplifier_tuner, self.stock_location
        )
        self.assertAlmostEqual(
            qty_amplifier_tuner, 1.0, msg="There should be one phono amplifier in stock"
        )

    def test_unbuild_no_stock(self):
        """
        No stock, missing component in product that should be dismantled.
        Should raise an exception.
        """
        # Create the amplifier first
        inventory_matrix = {
            self.product_amp_case: ["000124", ],
            self.product_amp_preamp: ["100457", ],
            self.product_amp_power_amp: ["200790", ],
            self.product_amp_tuner: ["400655", ],
        }
        self._set_inventory(inventory_matrix)
        manufacturing_order_no_phono = self._create_manufacturing_order(
            self.product_amplifier_tuner, 1.0, self.amplifier_bom
        )
        manufacturing_order_no_phono.action_assign()
        produce_wiz = (
            self.env["mrp.product.produce"]
            .with_context(active_id=manufacturing_order_no_phono.id)
            .create({})
        )
        lot_order_no_phono = self._create_lot_number(
            self.product_amplifier_tuner, "50002"
        )
        produce_wiz.lot_id = lot_order_no_phono
        produce_wiz.do_produce()
        # Then, try to build a product with phono option (which is out of stock)
        rebuild_order = self.env["mrp.unbuild.rebuild.variant"].create(
            {
                "unbuild_bom_id": self.amplifier_bom.id,
                "unbuild_product_id": self.product_amplifier_tuner.id,
                "unbuild_lot_id": lot_order_no_phono.id,
                "quantity": 1.0,
                "rebuild_bom_id": self.amplifier_bom.id,
                "rebuild_product_id": self.product_amplifier_phono.id,
            }
        )
        # As there's no phono product in stock, the rebuild should raise an exception
        with self.assertRaises(exceptions.ValidationError):
            rebuild_order.process()
        # Now, try to dismantle product with all options instead
        rebuild_order = self.env["mrp.unbuild.rebuild.variant"].create(
            {
                "unbuild_bom_id": self.amplifier_bom.id,
                "unbuild_product_id": self.product_amplifier_phono_tuner.id,
                "unbuild_lot_id": self.lot_50001.id,
                "quantity": 1.0,
                "rebuild_bom_id": self.amplifier_bom.id,
                "rebuild_product_id": self.product_amplifier_phono.id,
            }
        )
        unbuilt_lots = self.amplifier_phono_tuner_50001_mo.move_raw_ids.mapped(
            "active_move_line_ids.lot_id"
        )
        rebuild_order.process()

        # Phono amplifier should have been created
        qty_amplifier_phono = self.env["stock.quant"]._get_available_quantity(
            self.product_amplifier_phono, self.stock_location
        )
        self.assertAlmostEqual(
            qty_amplifier_phono, 1.0, msg="There should be one phono amplifier in stock"
        )

        # Get the manufacturing order
        finished_move_lines = self.env["stock.move.line"].search(
            [
                ("product_id", "=", self.product_amplifier_tuner.id),
                ("lot_id", "=", rebuild_order.rebuild_lot_id.id),
            ]
        )
        manufacturing_orders = finished_move_lines.mapped("production_id")
        manufacturing_order_phono = self.env["mrp.production"].search(
            [("id", "in", manufacturing_orders.ids), ],
            order="date_finished desc",
            limit=1,
        )
        # Ensure all SN in both the manufacturing orders are the same
        built_lots = manufacturing_order_phono.move_raw_ids.mapped(
            "active_move_line_ids.lot_id"
        )
        self.assertTrue(built_lots <= unbuilt_lots)
