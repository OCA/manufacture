# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "BOM Attribute Match Duplicate Kit",
    "version": "14.0.1.1.0",
    "category": "Manufacturing",
    "author": "Cetmix, Ooops, Odoo Community Association (OCA)",
    "summary": "BOM Attribute Match Duplicate Kit",
    "maintainers": ["aleuffre"],
    "depends": ["mrp_bom_attribute_match"],
    "license": "AGPL-3",
    "website": "https://github.com/OCA/manufacture",
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/product_template_views.xml",
        "wizard/product_template_kit_wizard.xml",
    ],
    "demo": [
        "demo/res_users_demo.xml",
    ],
}
