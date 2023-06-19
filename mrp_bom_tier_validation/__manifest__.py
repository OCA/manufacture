# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "MRP BOM Tier Validation",
    "summary": "Extends the functionality of Bill of Material to "
    "support a tier validation process.",
    "version": "15.0.1.0.0",
    "category": "Manufacture",
    "website": "https://github.com/OCA/manufacture",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["mrp", "base_tier_validation"],
    "data": [
        "views/mrp_bom_views.xml",
        "views/mrp_production_views.xml",
    ],
    "application": False,
    "installable": True,
}
