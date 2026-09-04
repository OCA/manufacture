# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "MRP Secondary Unit",
    "summary": "Manufacture products in a secondary unit",
    "version": "18.0.1.0.0",
    "development_status": "Beta",
    "category": "Manufacturing",
    "license": "AGPL-3",
    "author": "Quartile, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "depends": ["mrp", "stock_secondary_unit"],
    "data": [
        "views/mrp_bom_views.xml",
        "views/mrp_production_views.xml",
        "report/mrp_production_templates.xml",
    ],
    "maintainers": ["aungkokolin1997"],
    "installable": True,
    "auto_install": True,
}
