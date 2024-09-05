{
    "name": "Subcontracting Partner Management",
    "version": "16.0.1.1.0",
    "summary": "Subcontracting Partner Management",
    "author": "Ooops404, Cetmix, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "category": "Inventory",
    "website": "https://github.com/OCA/manufacture",
    "depends": ["purchase_stock", "mrp_subcontracting", "sale_stock"],
    "data": [
        "views/res_partner_views.xml",
        "views/stock_picking_type_views.xml",
    ],
    "installable": True,
    "application": False,
}
