# Copyright (C) 2021, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Product BOM Cost Rollup",
    "version": "13.0.1.0.0",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "summary": """Update BOM costs by rolling up. Adds scheduled job for
                  unattended rollups.""",
    "license": "AGPL-3",
    "category": "Product",
    "maintainer": "dreispt",
    "development_status": "Alpha",
    "website": "https://github.com/OCA/manufacture",
    "depends": ["mrp_account", "stock_account"],
    "data": [
        "views/product_views.xml",
        "views/mrp_bom.xml",
        "views/res_config_settings.xml",
        "data/cost_rollup_scheduler.xml",
        "data/email_template.xml",
    ],
    "installable": True,
}
