# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "MRP split",
    "summary": "Allows to split MO based on the available quantities.",
    "version": "9.0.1.0.0",
    "category": "Manufacturing",
    "website": "https://odoo-community.org/",
    "author": "Eficent, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["mrp", "stock_available_unreserved"],
    "data": [
        "wizards/mrp_split_view.xml",
        "views/mrp_production_view.xml",
    ],
}
