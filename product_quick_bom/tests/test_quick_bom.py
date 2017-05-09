# -*- coding: utf-8 -*-
#   Copyright (C) 2015 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
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

        computer = self.computer
        ram = self.ram
        hard_drive = self.hard_drive
        cpu = self.cpu
        computer.bom_line_ids = [
            (0, 0, {'product_id': ram.id, 'product_qty': 2, }),
            (0, 0, {'product_id': hard_drive.id, 'product_qty': 2, }),
            (0, 0, {'product_id': cpu.id, 'product_qty': 1, })
        ]

        bom = self.env['mrp.bom'].search([('product_id', '=', computer.id)])
        self.assertIsNotNone(bom)

    def test_read_bom(self):
        computer = self.computer
        ram = self.ram
        hard_drive = self.hard_drive
        cpu = self.cpu

        bom = self.env['mrp.bom'].create({
            'type': 'normal',
            'product_tmpl_id': computer.id})
        bomline1 = self.env['mrp.bom.line'].create({
            'product_id': ram.id,
            'product_qty': 2,
            'bom_id': bom.id,
        })
        bomline2 = self.env['mrp.bom.line'].create({
            'product_id': hard_drive.id,
            'product_qty': 2,
            'bom_id': bom.id,
        })
        bomline3 = self.env['mrp.bom.line'].create({
            'product_id': cpu.id,
            'product_qty': 1,
            'bom_id': bom.id,
        })

        self.assertTrue(bomline1 in computer.bom_line_ids)
        self.assertTrue(bomline2 in computer.bom_line_ids)
        self.assertTrue(bomline3 in computer.bom_line_ids)
