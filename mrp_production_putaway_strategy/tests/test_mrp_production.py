# Copyright 2017-18 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class MrpProductionCase(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(MrpProductionCase, self).setUp(*args, **kwargs)

        self.warehouse = self.env["stock.warehouse"].create(
            {
                "name": "X Warehouse",
                "code": "X WH",
                "reception_steps": "one_step",
                "delivery_steps": "ship_only",
            }
        )

        self.category = self.env["product.category"].create({"name": "Test"})

        self.loc_stock = self.warehouse.lot_stock_id
        self.bin_loc_stock = self.env["stock.location"].create(
            {"name": "Bin 1", "location_id": self.loc_stock.id, "usage": "internal"}
        )

        self.product1 = self.env.ref("mrp.product_product_computer_desk")
        self.product1.categ_id = self.category
        self.bom1 = self.env.ref("mrp.mrp_bom_desk")

        self.putaway_strategy = self.env["stock.putaway.rule"].create(
            {
                "product_id": self.product1.id,
                "location_in_id": self.loc_stock.id,
                "location_out_id": self.bin_loc_stock.id,
            }
        )
        self.loc_stock.putaway_rule_ids = self.putaway_strategy

    def _create_mo(
        self,
        product=False,
        bom=False,
        src_loc=False,
        dest_loc=False,
        qty=10.0,
        uom=False,
    ):
        if not product:
            product = self.product1
        uom = product.uom_id or uom
        if not bom:
            bom = self.bom1
        if not src_loc:
            src_loc = self.loc_stock
        if not dest_loc:
            dest_loc = self.loc_stock
        res = {
            "product_id": product.id,
            "bom_id": bom.id,
            "location_src_id": src_loc.id,
            "location_dest_id": dest_loc.id,
            "product_qty": qty,
            "product_uom_id": uom.id,
        }
        return self.env["mrp.production"].create(res)

    def test_putaway_strategy_01(self):
        """Tests if the putaway strategy applies to a Manufacturing Order."""
        # Create MO
        mo = self._create_mo()
        for finished in mo.move_finished_ids:
            self.assertEqual(
                finished.location_dest_id,
                self.bin_loc_stock,
                "Putaway strategy hasn't been applied.",
            )
