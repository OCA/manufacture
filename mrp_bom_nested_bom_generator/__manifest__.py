{
    "name": "Nested BOM Generator",
    "summary": "Nested BOM Generator",
    "author": "Cetmix, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "category": "Manufacturing",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["mrp"],
    "demo": [
        "data/demo.xml",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/product_template_views.xml",
        "views/mrp_nested_bom_views.xml",
    ],
    "installable": True,
}
