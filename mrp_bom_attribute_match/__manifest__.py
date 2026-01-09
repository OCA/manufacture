{
    "name": "BOM Attribute Match",
    "version": "17.0.1.0.1",
    "category": "Manufacturing",
    "author": "Ilyas, Ooops, Odoo Community Association (OCA)",
    "summary": "Dynamic BOM component based on product attribute",
    "depends": ["mrp", "mrp_plm"],
    "license": "AGPL-3",
    "website": "https://github.com/OCA/manufacture",
    "data": [
        "views/mrp_bom_views.xml",
        "views/mrp_plm_views.xml",
    ],
    "installable": True,
    "auto_install": True,
    "post_init_hook": "_post_init_hook",
}