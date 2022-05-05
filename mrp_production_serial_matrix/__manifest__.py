# Copyright 2021 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "MRP Production Serial Matrix",
    "version": "14.0.1.1.0",
    "category": "Manufacturing",
    "license": "AGPL-3",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "depends": [
        "mrp",
        "web_widget_x2many_2d_matrix",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizards/mrp_production_serial_matrix_view.xml",
        "views/mrp_production_views.xml",
    ],
    "installable": True,
}
