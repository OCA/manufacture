# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Quentin Dupont (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "MRP BoM Product Price Margin",
    "summary": "Handle Product Standard, Sale Price and Margin with its BoM cost",
    "version": "16.0.1.0.0",
    "category": "GRAP - Custom",
    "author": "GRAP, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "license": "AGPL-3",
    "depends": [
        "mrp",
        # OCA modules
        "product_standard_margin",
    ],
    "data": [
        "views/view_mrp_bom.xml",
    ],
    "installable": True,
}
