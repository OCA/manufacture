# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Workcenter Scrap Reason Code",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "summary": "Filter allowed reason codes with workcenter assigned.",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "category": "Manufacturing",
    "depends": ["mrp", "scrap_reason_code"],
    "data": [
        "views/reason_code_view.xml",
    ],
    "installable": True,
}
