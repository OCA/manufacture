# Copyright 2025 Tecnativa - Christian Ramos
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "BoM Product Allergen",
    "summary": "Add allergen information to bill of materials",
    "version": "18.0.1.0.0",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "license": "AGPL-3",
    "category": "Manufacturing",
    "depends": ["mrp", "product_allergen"],
    "data": [
        "report/mrp_report_bom_structure.xml",
        "views/product_views.xml",
        "views/mrp_bom_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "mrp_bom_product_allergen/static/src/xml/mrp_bom_overview_allergen.xml",
        ],
    },
    "installable": True,
}
