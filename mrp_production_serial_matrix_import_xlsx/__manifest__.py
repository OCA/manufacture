# Copyright 2026 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "MRP Production Serial Matrix Import Xlsx",
    "version": "17.0.1.0.0",
    "category": "Manufacturing",
    "license": "AGPL-3",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "depends": [
        "mrp_production_serial_matrix",
    ],
    "data": [
        "views/mrp_production_serial_matrix_views.xml",
    ],
    "external_dependencies": {
        "python": [
            "openpyxl",
        ],
    },
    "installable": True,
}
