# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "MRP BoM Current Stock",
    "summary": "Add a report that explodes the bill of materials and show the "
               "stock available in the source location.",
    "version": "9.0.1.0.0",
    "category": "Manufacture",
    "website": "https://odoo-community.org/",
    "author": "Eficent, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "mrp_bom_location",
    ],
    "data": [
        "reports/report_mrpcurrentstock.xml",
        "wizard/bom_route_current_stock_view.xml",
    ],
}
