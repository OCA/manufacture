# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "MRP Subcontracting Auto Create Lot",
    "summary": "Auto create lots when recording the subcontracting consumption.",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "category": "Manufacturing",
    "version": "16.0.1.0.1",
    "license": "AGPL-3",
    "depends": ["mrp_subcontracting", "mrp_auto_create_lot"],
    "data": ["views/mrp_production_views.xml"],
    "application": False,
    "installable": True,
}
