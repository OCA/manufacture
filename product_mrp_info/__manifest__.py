# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Product MRP Info",
    "version": "12.0.1.0.0",
    "development_status": "Beta",
    "license": "LGPL-3",
    "author": "Eficent, Odoo Community Association (OCA)",
    "maintainers": ["lreficent"],
    "summary": "Adds smart button in product form view linking to "
               "manufacturing order list.",
    "website": "https://github.com/OCA/manufacture",
    "category": "Manufacturing",
    "depends": [
        "mrp",
    ],
    "data": [
        "views/product_views.xml",
    ],
    "installable": True,
    "application": False,
}
