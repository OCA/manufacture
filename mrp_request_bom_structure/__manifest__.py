# © 2020 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "MRP Request Bom Structure",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Akretion,"
              "Odoo Community Association (OCA)",
    "summary": "Shortcut between Manufacturing Request and Bom report",
    "website": "https://github.com/OCA/manufacture",
    "category": "Manufacturing",
    "depends": [
        "mrp_production_request",
    ],
    "data": [
        "data/config_parameter.xml",
        "views/mrp_request.xml",
    ],
    "installable": True
}
