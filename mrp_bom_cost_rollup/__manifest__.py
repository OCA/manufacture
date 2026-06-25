# Copyright 2026 Cubiczan
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "MRP BoM Cost Rollup",
    "version": "18.0.1.0.0",
    "category": "Manufacturing",
    "summary": "Roll up Bill of Materials component and operation costs and "
    "write the result to the manufactured product's cost",
    "author": "Cubiczan, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "license": "AGPL-3",
    "maintainers": ["icohangar-ops"],
    "development_status": "Beta",
    "depends": ["mrp"],
    "data": [
        "views/mrp_bom_views.xml",
        "views/product_views.xml",
    ],
    "installable": True,
}
