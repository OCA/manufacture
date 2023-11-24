{
    "name": "BOM Attribute Match Semifinished Products",
    "version": "14.0.1.0.0",
    "category": "Manufacturing",
    "author": "Cetmix, Ooops, Odoo Community Association (OCA)",
    "summary": "BOM Attribute Match Semifinished Products",
    "depends": ["mrp_bom_attribute_match"],
    "maintainers": ["geomer198", "CetmixGitDrone"],
    "license": "AGPL-3",
    "website": "https://github.com/OCA/manufacture",
    "data": [
        "security/semifinished_product_security.xml",
        "security/ir.model.access.csv",
        "views/product_template_views.xml",
        "views/semi_finished_product_template_line_views.xml",
        "wizard/finished_product_structure_wizard.xml",
    ],
}
