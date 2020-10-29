# Copyright 2018-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "MRP Stock Orderpoint Manual Procurement",
    "summary": "Updates the value of MO Responsible and keeps track"
    "of changes regarding this field",
    "version": "13.0.1.0.0",
    "author": "Forgeflow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "category": "Manufacturing",
    "depends": ["mrp", "stock_orderpoint_manual_procurement"],
    "data": ["views/mrp_production_view.xml"],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "auto_install": True,
}
