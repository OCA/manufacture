# Copyright 2020 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import TransactionCase


class TestMrpAutoCreateLot(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(TestMrpAutoCreateLot, self).setUp(*args, **kwargs)
        self.production_model = self.env['mrp.production']
        self.bom_model = self.env['mrp.bom']
        self.picking_model = self.env['stock.picking']
        self.stock_location_stock = self.env.ref('stock.stock_location_stock')
        self.manufacture_route = self.env.ref('mrp.route_warehouse0_manufacture')
        self.uom_unit = self.env.ref('uom.product_uom_unit')

        self.workcenter = self.env['mrp.workcenter'].create({
            'costs_hour': 10,
            'name': 'Workcenter',
        })
        self.routing_id = self.env['mrp.routing'].create({
            'name': 'Routing',
        })
        self.operation = self.env['mrp.routing.workcenter'].create({
            'name': 'operation',
            'workcenter_id': self.workcenter.id,
            'routing_id': self.routing_id.id,
            'time_mode': 'manual',
            'time_cycle_manual': 20,
            'batch': 'no',
            'sequence': 1,
        })

        self.product_manuf = self.env['product.product'].create({
            'name': 'Manuf',
            'type': 'product',
            'uom_id': self.uom_unit.id,
            'route_ids': [(6, 0, self.manufacture_route.ids)],
            'tracking': 'lot',
            'auto_create_lot': True,
        })
        self.product_raw_material = self.env['product.product'].create({
            'name': 'Raw Material',
            'type': 'product',
            'uom_id': self.uom_unit.id,
        })

        self.bom = self.env['mrp.bom'].create({
            'product_id': self.product_manuf.id,
            'product_tmpl_id': self.product_manuf.product_tmpl_id.id,
            'type': 'normal',
            'routing_id': self.routing_id.id,
            'bom_line_ids': ([
                (0, 0, {
                    'product_id': self.product_raw_material.id,
                    'product_qty': 1,
                    'product_uom_id': self.uom_unit.id,
                }),
            ])
        })

    def test_01_manufacture_auto_create_lot(self):
        production = self.production_model.create({
            'product_id': self.product_manuf.id,
            'product_qty': 1,
            'product_uom_id': self.uom_unit.id,
            'bom_id': self.bom.id,
        })
        production.button_plan()
        self.assertEqual(production.workorder_count, 1)

        workorders = production.workorder_ids
        for workorder in workorders:
            workorder.button_start()
            workorder.record_production()
            self.assertEqual(workorder.state, 'done')
