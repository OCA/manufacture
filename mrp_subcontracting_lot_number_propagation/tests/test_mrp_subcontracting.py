# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests.common import Form

from odoo.addons.mrp_lot_number_propagation.tests.common import Common


class TestMrpSubcontracting(Common):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.subcontracted_bom = cls._get_subcontracted_bom()
        cls.vendor = cls.env.ref("base.res_partner_12")
        cls._update_stock_component_qty(
            bom=cls.subcontracted_bom,
            location=cls.vendor.property_stock_subcontractor,
        )
        with Form(cls.env["stock.picking"]) as form:
            form.picking_type_id = cls.env.ref("stock.picking_type_in")
            form.partner_id = cls.vendor
            with form.move_ids_without_package.new() as move:
                variant = cls.subcontracted_bom.product_tmpl_id.product_variant_ids
                move.product_id = variant
                move.product_uom_qty = 1
            cls.picking = form.save()
            cls.picking.action_confirm()

    @classmethod
    def _get_subcontracted_bom(cls):
        bom = cls.env.ref("mrp_subcontracting.mrp_bom_subcontract")
        bom.product_tmpl_id.tracking = "serial"
        bom.bom_line_ids.unlink()
        bom.bom_line_ids.create(
            {
                "bom_id": bom.id,
                "product_id": cls.product_tracked_by_sn.id,
                "product_qty": 1,
                "propagate_lot_number": True,
            }
        )
        bom.lot_number_propagation = True
        return bom

    def test_lot_propagation(self):
        order = self.picking.move_lines.move_orig_ids.production_id
        self.assertEqual(order.bom_id, self.subcontracted_bom)
        # Fill the 'qty_done' for consumed components through
        # the "Record Components" form
        view_ref = "mrp_subcontracting.mrp_production_subcontracting_form_view"
        self.assertFalse(order.propagated_lot_producing)
        with Form(order, view_ref) as form:
            for i in range(len(order.move_line_raw_ids)):
                with form.move_line_raw_ids.edit(i) as move_line:
                    move_line.qty_done = move_line.product_uom_qty
            order = form.save()
        self.assertEqual(order.propagated_lot_producing, self.LOT_NAME)
        # Set the quantity produced and consume the components, this will set
        # the expected serial number on the finished product to receive
        self.assertFalse(self.picking.move_line_ids.lot_id)
        order.qty_producing = order.product_qty
        order.subcontracting_record_component()
        lot = self.picking.move_line_ids.lot_id
        self.assertEqual(lot.name, self.LOT_NAME)
        # Receive the finished product in stock
        dest_location = self.picking.move_lines.location_dest_id
        quant_in_stock = self._get_lot_quants(lot, dest_location)
        self.assertFalse(quant_in_stock)
        self.picking._action_done()
        quant_in_stock = self._get_lot_quants(lot, dest_location)
        self.assertTrue(quant_in_stock)
