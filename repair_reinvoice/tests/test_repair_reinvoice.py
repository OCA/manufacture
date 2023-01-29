from odoo.tests import common
from odoo.fields import Date

class TestMrpRepairReinvoice(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestMrpRepairReinvoice, cls).setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test product",
                "standard_price": 10,
                "list_price": 20,
            }
        )
        cls.partner = cls.env.ref("base.res_partner_address_1")
        cls.location = cls.env["stock.location"].create(
            {
                "name": "Test location",
            }
        )
        cls.repair = cls.env["repair.order"].create(
            {
                "product_id": cls.product.id,
                "partner_id": cls.partner.id,
                "partner_invoice_id": cls.partner.id,
                "product_uom": cls.product.uom_id.id,
                "location_id": cls.location.id,
                "invoice_method": "after_repair",
            }
        )
        domain_location = [("usage", "=", "production")]
        stock_location_id = cls.env["stock.location"].search(domain_location, limit=1)
        cls.repair_line = cls.env["repair.line"].create(
            {
                "repair_id": cls.repair.id,
                "type": "add",
                "product_id": cls.product.id,
                "product_uom": cls.product.uom_id.id,
                "name": "Test line",
                "location_id": cls.repair.location_id.id,
                "location_dest_id": stock_location_id.id,
                "product_uom_qty": 1,
                "price_unit": 20,
            }
        )
    
    def test_reinvoice(self):
        self.repair.action_validate()
        self.repair.action_repair_start()
        self.repair.action_repair_end()
        self.repair.action_repair_invoice_create()
        self.assertEqual(self.repair.invoice_count, 1)
        self.assertEqual(self.repair.invoiced, True)
        self.repair.invoice_ids.action_post()
        today = Date.context_today(self.env.user)
        refund_invoice_wiz = self.env['account.move.reversal'].with_context(active_model="account.move", active_ids=[self.repair.invoice_ids.ids[0]]).create({
            'reason': 'Please reverse',
            'refund_method': 'cancel',
            'date': today,
        })
        refund_invoice = self.env['account.move'].browse(refund_invoice_wiz.reverse_moves()['res_id'])
        self.assertEqual(self.repair.invoice_count, 2)
        self.assertEqual(self.repair.invoiced, False)