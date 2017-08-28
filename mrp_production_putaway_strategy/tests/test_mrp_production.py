# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class MrpProductionCase(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(MrpProductionCase, self).setUp(*args, **kwargs)

        self.warehouse = self.env["stock.warehouse"].create({
            "name": "X Warehouse",
            "code": "X WH",
            "reception_steps": "one_step",
            "delivery_steps": "ship_only",
            "resupply_from_wh": False,
            "default_resupply_wh_id": False,
        })

        self.category = self.env['product.category'].create({'name': 'Test'})

        self.loc_stock = self.warehouse.lot_stock_id
        self.bin_loc_stock = self.env['stock.location'].create({
            'name': 'Bin 1',
            'location_id': self.loc_stock.id,
            'usage': 'internal'
        })

        self.putaway_strategy = self.env['product.putaway'].create({
            'name': 'Fixed Loc',
            'method': 'fixed',
            'fixed_location_ids': [(
                0, 0, {'fixed_location_id': self.bin_loc_stock.id,
                       'category_id': self.category.id})]
        })
        self.loc_stock.putaway_strategy_id = self.putaway_strategy

        self.loc_production = self.env.ref(
            "stock.location_production")
        self.product1 = self.env.ref("product.product_product_18")
        self.product1.categ_id = self.category
        self.bom1 = self.env.ref("mrp.mrp_bom_3")

    def _create_mo(self, product=False, bom=False, src_loc=False,
                   dest_loc=False, qty=10.0, uom=False, move_prod_id=False):
        if not product:
            product = self.product1
            uom = product.uom_id
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
            "product_uom": uom.id,
            "move_prod_id": move_prod_id.id if move_prod_id else False,
        }
        return self.env['mrp.production'].create(res)

    def test_putaway_strategy_01(self):
        """Tests if the putaway strategy applies to a Manufacturing Order
        without destination move."""
        # Create MO
        mo = self._create_mo()
        # Click confirm button
        mo.signal_workflow("button_confirm")
        for finished in mo.move_created_ids:
            self.assertEqual(
                finished.location_dest_id, self.bin_loc_stock,
                "Putaway strategy hasn't been applied.")

    def test_putaway_strategy_02(self):
        """Tests if the destination location is respected whenever a
        destination move is set for the Manufactuing Order."""
        # Create a destination transfer.
        move = self.env['stock.move'].create({
            "name": "Destination move for the test MO",
            "product_id": self.product1.id,
            "product_uom_qty": 10.0,
            "product_uom": self.product1.uom_id.id,
            "location_id": self.loc_stock.id,
            "location_dest_id": self.bin_loc_stock.id,
        })
        # Create MO
        mo = self._create_mo(move_prod_id=move)
        # Click confirm button
        mo.signal_workflow("button_confirm")
        for finished in mo.move_created_ids:
            self.assertEqual(
                finished.location_dest_id, self.loc_stock,
                "Destination move has not been respected.")
