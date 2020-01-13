# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "MRP BoM Equivalences",
    "summary": "Specify non-equivalent products to a part on a BOM",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "category": "MRP",
    "website": "http://www.opensourceintegrators.com",
    "depends": ["mrp", "product_priority", "product_equivalent_category"],
    "data": [
        "views/mrp_bom_view.xml",
    ],
    "installable": True,
}
