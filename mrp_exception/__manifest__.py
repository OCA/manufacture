# Copyright (C) 2024, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "MRP Exception",
    "summary": "Custom exceptions on mrp production",
    "version": "17.0.1.0.0",
    "category": "Generic Modules/Manufacturing Management",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "depends": ["mrp", "base_exception", "stock_exception"],
    "license": "AGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "data/mrp_exception_data.xml",
        "wizard/mrp_exception_confirm_view.xml",
        "views/mrp_view.xml",
    ],
    "installable": True,
}
