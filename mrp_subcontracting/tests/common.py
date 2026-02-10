# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
# Copyright 2019 Odoo
# Copyright 2020 Tecnativa - Alexandre Díaz
# Copyright 2020 Tecnativa - Pedro M. Baeza

from odoo.tests.common import SavepointCase


class TestMrpSubcontractingCommon(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        main_partner = cls.env['res.partner'].create({'name': 'main_partner'})
        cls.subcontractor_partner1 = cls.env['res.partner'].create({
            'name': 'subcontractor_partner',
            'parent_id': main_partner.id,
            'company_id': cls.env.ref('base.main_company').id,
        })

        cls.comp1 = cls.env['product.product'].create({
            'name': 'Component1',
            'type': 'product',
            'categ_id': cls.env.ref('product.product_category_all').id,
        })
        cls.comp2 = cls.env['product.product'].create({
            'name': 'Component2',
            'type': 'product',
            'categ_id': cls.env.ref('product.product_category_all').id,
        })
        cls.finished = cls.env['product.product'].create({
            'name': 'finished',
            'type': 'product',
            'categ_id': cls.env.ref('product.product_category_all').id,
        })
        cls.bom = cls.env['mrp.bom'].create({
            'type': 'subcontract',
            'product_tmpl_id': cls.finished.product_tmpl_id.id,
            'subcontractor_ids': [(4, cls.subcontractor_partner1.id)],
            'bom_line_ids': [
                (0, 0, {
                    'product_id': cls.comp1.id,
                    'product_qty': 1,
                }),
                (0, 0, {
                    'product_id': cls.comp2.id,
                    'product_qty': 1,
                }),
            ],
        })

        cls.comp2comp = cls.env['product.product'].create({
            'name': 'component for Component2',
            'type': 'product',
            'categ_id': cls.env.ref('product.product_category_all').id,
        })
        cls.comp2_bom = cls.env['mrp.bom'].create({
            'product_tmpl_id': cls.comp2.product_tmpl_id.id,
            'bom_line_ids': [
                (0, 0, {
                    'product_id': cls.comp2comp.id,
                    'product_qty': 1,
                }),
            ],
        })

        cls.warehouse = cls.env['stock.warehouse'].search([], limit=1)
