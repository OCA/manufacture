# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Purchase and Subcontracting Management",
    "version": "14.0.1.0.0",
    "category": "Manufacturing/Purchase",
    "summary": """
        This bridge module adds some smart buttons between Purchase and Subcontracting
    """,
    "author": "Odoo S.A., Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "depends": ["mrp_subcontracting", "purchase"],
    "data": [
        "views/purchase_order_views.xml",
        "views/stock_picking_views.xml",
    ],
    "installable": True,
    "auto_install": True,
    "license": "LGPL-3",
}
