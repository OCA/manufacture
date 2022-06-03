# © 2022 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "MRP BOM Vendor Price",
    "version": "12.0.1.0.0",
    "category": "Manufacturing",
    "website": "https://github.com/OCA/manufacture",
    "author": "Akretion,"
              "Odoo Community Association (OCA)",
    "maintainers": ["bealdav"],
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "mrp",
    ],
    "data": [
        "data/cron.xml",
        "views/product.xml",
        "views/bom.xml",
    ],
}
