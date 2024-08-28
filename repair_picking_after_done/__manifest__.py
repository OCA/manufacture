# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Repair picking after done",
    "version": "14.0.1.0.2",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "summary": "Transfer repaired move to another location directly from repaire order",
    "category": "Repair",
    "depends": ["repair_type", "repair_stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/repair.xml",
        "wizards/repair_move_transfer_views.xml",
    ],
    "installable": True,
    "development_status": "Alpha",
    "license": "AGPL-3",
    "application": False,
}
