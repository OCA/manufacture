# Copyright (C) 2021 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

{
    "name": "Repair Purchase Return",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "license": "LGPL-3",
    "category": "Repair",
    "summary": "Create a Purchase Return from a Repair",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "depends": ["repair", "purchase_return"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/repair_purchase_return_wiz_views.xml",
        "views/repair_order_views.xml",
        "views/purchase_return_order_views.xml",
    ],
    "maintainers": ["JordiBForgeFlow"],
    "installable": True,
    "application": False,
}
