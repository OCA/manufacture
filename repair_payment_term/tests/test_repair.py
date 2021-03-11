# Copyright 2021 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.repair.tests.test_repair import TestRepair
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class PaymentTestRepair(TestRepair):

    def test_00_repair_payment_term(self):
        partner_12 = self.env.ref('base.res_partner_12')
        payment_term_id = self.env.ref('account.account_payment_term')
        partner_12.property_payment_term_id = payment_term_id

        repair = self._create_simple_repair_order('after_repair')
        repair.onchange_partner_id()
        self.assertEqual(
            repair.payment_term_id,
            payment_term_id,
            'Repair onchange payment term not working.'
        )
        self._create_simple_operation(
            repair_id=repair.id, qty=1.0, price_unit=50.0)
        # I confirm Repair order taking Invoice Method 'After Repair'.
        repair.sudo(self.res_repair_user.id).action_repair_confirm()

        # I check the state is in "Confirmed".
        self.assertEqual(repair.state, "confirmed",
                         'Repair order should be in "Confirmed" state.')
        repair.action_repair_start()

        # I check the state is in "Under Repair".
        self.assertEqual(repair.state, "under_repair",
                         'Repair order should be in "Under_repair" state.')

        # Repairing process for product is in Done state and I end
        # Repair process by clicking on "End Repair" button.
        repair.action_repair_end()

        # I define Invoice Method 'After Repair'
        # option in this Repair order.so I create
        # invoice by clicking on "Make Invoice" wizard.
        make_invoice = self.RepairMakeInvoice.create({
            'group': True})
        # I click on "Create Invoice" button of this wizard to make invoice.
        context = {
            "active_model": 'repair_order',
            "active_ids": [repair.id],
            "active_id": repair.id
        }
        make_invoice.with_context(context).make_invoices()

        # I check that invoice is created for this Repair order.
        self.assertEqual(
            len(repair.invoice_id), 1,
            "No invoice exists for this repair order"
        )
        self.assertEqual(
            repair.invoice_id.payment_term_id,
            repair.payment_term_id,
            "Repair Payment Term and Invoice is not the same"
        )
        self.assertEqual(
            len(repair.move_id.move_line_ids[0].consume_line_ids),
            1, "Consume lines should be set"
        )
