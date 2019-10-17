# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "MRP Work Order Sequence",
    "summary": "adds sequence to production work orders.",
    "version": "12.0.1.0.0",
    "category": "Manufacturing",
    "author": "Eficent, "
              "Odoo Community Association (OCA)",
    "development_status": "Beta",
    "maintainers": ["lreficent"],
    "website": "https://github.com/OCA/manufacture",
    "license": "LGPL-3",
    "depends": [
        "mrp",
    ],
    "data": [
        "views/mrp_workorder_view.xml",
    ],
    "installable": True,
}
