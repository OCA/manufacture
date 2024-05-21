# Copyright 2019-23 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "MRP Multi Level Estimate",
    "version": "17.0.1.0.0",
    "development_status": "Production/Stable",
    "license": "LGPL-3",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "maintainers": ["LoisRForgeFlow"],
    "summary": "Allows to consider demand estimates using MRP multi level.",
    "website": "https://github.com/OCA/manufacture",
    "category": "Manufacturing",
    "depends": ["mrp_multi_level", "stock_demand_estimate"],
    "data": ["views/product_mrp_area_views.xml", "views/mrp_area_views.xml"],
    "installable": True,
    "application": False,
    "auto_install": True,
}
