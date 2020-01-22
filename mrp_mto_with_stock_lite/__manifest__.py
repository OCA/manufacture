# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "MRP MTO with Stock (Lite)",
    "summary": "Module needed to make stock_mts_mto_rule module compatible "
               "with mrp module.",
    "author": "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "category": "Manufacturing",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    'auto_install': False,
    "depends": [
        "stock",
        "mrp",
        "stock_mts_mto_rule",
    ],
    "demo": [
        'demo/product.xml',
    ],
}
