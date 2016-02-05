# -*- coding: utf-8 -*-
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.tests import common


class TestMrpProductionPartnerNote(common.TransactionCase):

    def setUp(self):
        super(TestMrpProductionPartnerNote, self).setUp()
        self.note = "This is a test production note"
        self.procurement_model = self.env['procurement.order']
        self.product = self.browse_ref('product.product_product_18')
        self.product.route_ids = [
            (4, self.ref('mrp.route_warehouse0_manufacture')),
            (4, self.ref('stock.route_warehouse0_mto'))]
        self.partner = self.browse_ref('base.res_partner_2')
        self.partner.write({
            'mrp_notes': self.note})

    def test_production_notes(self):
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'order_line': [(0, 0, {
                'name': self.product.name,
                'product_id': self.product.id,
                'product_uom_qty': 2,
                'product_uom': self.product.uom_id.id,
                'price_unit': self.product.list_price})],
            'pricelist_id': self.env.ref('product.list0').id,
        })
        sale_order.action_confirm()
        procurement = self.procurement_model.search(
            [('sale_line_id', 'in', sale_order.mapped('order_line').ids)])
        procurements = self.procurement_model.search(
            [('group_id', '=', procurement.group_id.id)])
        procurements.run()
        productions = procurements.mapped('production_id')
        for note in productions.mapped('notes'):
            self.assertEqual(
                "<p>%s</p>" % (self.note), note,
                "MO note must be the same as '%s'" % (note))
            self.assertEqual(
                self.partner.mrp_notes, note,
                "MO note must be taken from partner")
