# Copyright 2021 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": "MRP Repair Vendor Refund",
    "summary": "Allow to get refunds from your vendors for repairs done by "
    "your company",
    "version": "14.0.1.0.0",
    "category": "Manufacturing",
    "website": "https://github.com/OCA/manufacture",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "installable": True,
    "depends": ["repair"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/repair_line_update_vendor_to_refund_qty_views.xml",
        "wizards/repair_fee_update_vendor_to_refund_qty_views.xml",
        "views/account_move_views.xml",
        "views/repair_views.xml",
    ],
}
