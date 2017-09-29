# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "MRP BOM Location",
    "summary": "Adds location field to Bill of Materials and its components.",
    "version": "9.0.1.0.0",
    "category": "Manufacture",
    "website": "https://odoo-community.org/",
    "author": "Eficent, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "mrp",
    ],
    "data": [
        "views/mrp_view.xml",
        "views/report_mrpbomstructure.xml",
    ],
}
