{
    "name": "Purchase and Subcontracting Management",
    "summary": """
        This bridge module adds some smart buttons between Purchase and Subcontracting
    """,
    "website": "https://github.com/OCA/manufacture",
    "version": "14.0.1.0.0",
    "author": "Odoo S.A., Ooops, Cetmix, Odoo Community Association (OCA)",
    "maintainers": ["dessanhemrayev", "CetmixGitDrone", "Volodiay622", "geomer198"],
    "category": "Manufacturing/Purchase",
    "depends": ["mrp_subcontracting", "purchase_mrp", "stock_dropshipping"],
    "data": [
        "data/mrp_subcontracting_dropshipping_data.xml",
        "views/purchase_order_views.xml",
        "views/stock_picking_views.xml",
    ],
    "demo": [
        "demo/product_category_demo.xml",
        "demo/stock_location_demo.xml",
        "demo/partner_subcontract_demo.xml",
        "demo/product_product_demo.xml",
        "demo/product_supplierinfo_demo.xml",
        "demo/bom_subcontract_demo.xml",
        "demo/stock_rules_demo.xml",
    ],
    "installable": True,
    "auto_install": True,
    "license": "LGPL-3",
}
