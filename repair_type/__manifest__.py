# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Repair Type",
    "version": "14.0.1.0.2",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "summary": "Repair type",
    "category": "Repair",
    "depends": ["repair"],
    "data": [
        "views/repair.xml",
        "views/repair_type.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "development_status": "Alpha",
    "license": "AGPL-3",
    "application": False,
}
