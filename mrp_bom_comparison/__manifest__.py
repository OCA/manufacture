# -*- coding: utf-8 -*-
# Copyright 2018 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Bill of Materials comparison",
    "summary": "Compare two Bill of Materials to view the differences",
    "version": "10.0.1.0.0",
    "category": "Manufacturing",
    "website": "https://github.com/OCA/manufacture",
    "author": "ABF OSIELL, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "mrp",
        "report",
    ],
    "data": [
        "wizards/mrp_bom_comparison.xml",
        "reports/mrp_bom_comparison.xml",
        "reports.xml",
    ],
}
