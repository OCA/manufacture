# Copyright 2019-20 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/Agpl.html).

{
    "name": "MRP Multi Level Estimate",
    "version": "14.0.1.0.2",
    "development_status": "Beta",
    "license": "AGPL-3",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "maintainers": ["LoisRForgeFlow"],
    "summary": "Allows to consider demand estimates using MRP multi level.",
    "website": "https://github.com/OCA/manufacture",
    "category": "Manufacturing",
    "depends": ["mrp_multi_level", "stock_demand_estimate_matrix"],
    "data": ["views/product_mrp_area_views.xml"],
    "installable": True,
    "application": False,
    "auto_install": True,
}
