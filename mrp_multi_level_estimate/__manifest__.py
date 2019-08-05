# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/Agpl.html).

{
    "name": "MRP Multi Level Estimate",
    "version": "12.0.1.0.0",
    "development_status": "Beta",
    "license": "AGPL-3",
    "author": "Eficent, "
              "Odoo Community Association (OCA)",
    "maintainers": ["lreficent"],
    "summary": "Allows to consider demand estimates using MRP multi level.",
    "website": "https://github.com/OCA/manufacture",
    "category": "Manufacturing",
    "depends": [
        "mrp_multi_level",
        "stock_demand_estimate",
    ],
    "data": [
        "views/product_mrp_area_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": True,
}
