# Copyright 2020 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "MRP Request Workcenter Cycle",
    "version": "12.0.1.0.0",
    "category": "Manufacturing",
    "license": "AGPL-3",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture/tree/12.0"
    "/mrp_request_workcenter_cycle",
    "depends": [
        "mrp_production_request",
    ],
    "development_status": "Alpha",
    "data": [
        "security/ir.model.access.csv",
        "views/product.xml",
        "views/request.xml",
    ],
    "demo": [
        "demo/workcenter.xml",
        "demo/request.xml",
    ],
    "maintainers": ["bealdav"],
    "installable": True,
}
