# Copyright (C) 2023 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from odoo import SUPERUSER_ID, api


def fill_invoice_ids(env):
    """Fill new field invoice_ids with invoice_id and with credit notes
    from reversed invoices"""
    invoiced_repair_ids = env["repair.order"].search([("invoice_id", "!=", False)])
    for invoiced_repair in invoiced_repair_ids:
        invoice_id = invoiced_repair.invoice_id
        invoiced_repair.invoice_ids += invoice_id
        if invoice_id.payment_state == "reversed":
            refunds = env["account.move"].search(
                [
                    ("move_type", "=", "out_refund"),
                    ("reversed_entry_id", "=", invoice_id.id),
                ]
            )
            invoiced_repair.invoice_ids += refunds


def post_init_hook(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        fill_invoice_ids(env)
