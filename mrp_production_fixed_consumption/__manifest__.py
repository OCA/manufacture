# Copyright 2026 Jarsa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "MRP Production Fixed Consumption",
    "summary": "Consume the planned component quantities even when the "
    "produced quantity is lower",
    "version": "19.0.1.0.0",
    "category": "Manufacturing",
    "website": "https://github.com/OCA/manufacture",
    "author": "Jarsa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["mrp"],
    "data": ["views/mrp_bom_views.xml"],
    "installable": True,
    "maintainers": ["alan196"],
}
