# -*- coding: utf-8 -*-
#   Copyright (C) 2015 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
import logging
_logger = logging.getLogger(__name__)


class TestQuickBom(TransactionCase):

    def setUp(self):
        super(TestQuickBom, self).setUp()
        self.computer = self.env.ref(
            'product.product_product_5_product_template')
        self.ram = self.env.ref('product.product_product_13_product_template')
        self.hard_drive = self.env.ref(
            'product.product_product_17_product_template')
        self.cpu = self.env.ref('product.product_product_22_product_template')

    def test_create_bom(self):
        self.computer.write({'bom_line_ids': [
            (0, 0, {'product_id': self.ram.id, 'product_qty': 2, }),
            (0, 0, {'product_id': self.hard_drive.id, 'product_qty': 2, }),
            (0, 0, {'product_id': self.cpu.id, 'product_qty': 1, })]})
        bom = self.computer.bom_ids
        self.assertEqual(self.computer.id, bom.product_tmpl_id.id)
        self.assertEqual(bom.bom_line_ids[0].product_id.id, self.ram.id)
        self.assertEqual(bom.bom_line_ids[0].product_qty, 2)
        self.assertEqual(bom.bom_line_ids[1].product_id.id, self.hard_drive.id)
        self.assertEqual(bom.bom_line_ids[1].product_qty, 2)
        self.assertEqual(bom.bom_line_ids[2].product_id.id, self.cpu.id)
        self.assertEqual(bom.bom_line_ids[2].product_qty, 1)

    def test_read_bom(self):
        bom = self.env['mrp.bom'].create({
            'type': 'normal',
            'product_tmpl_id': self.computer.id})
        bomline1 = self.env['mrp.bom.line'].create({
            'product_id': self.ram.id,
            'product_qty': 2,
            'bom_id': bom.id,
        })
        bomline2 = self.env['mrp.bom.line'].create({
            'product_id': self.hard_drive.id,
            'product_qty': 2,
            'bom_id': bom.id,
        })
        bomline3 = self.env['mrp.bom.line'].create({
            'product_id': self.cpu.id,
            'product_qty': 1,
            'bom_id': bom.id,
        })

        self.assertTrue(bomline1 in self.computer.bom_line_ids)
        self.assertTrue(bomline2 in self.computer.bom_line_ids)
        self.assertTrue(bomline3 in self.computer.bom_line_ids)
