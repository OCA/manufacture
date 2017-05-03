# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2015 John Walsh
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "MRP MTO with Stock",
    "summary": "Fix Manufacturing orders to pull from stock until qty is "
               "zero, and then create a procurement for them.",
    "author": "John Walsh, Eficent, Odoo Community Association (OCA)",
    "website": "https://odoo-community.org/",
    "category": "Manufacturing",
    "version": "9.0.1.0.0",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["mrp"],
    "data": ['views/product_template_view.xml'],
}
