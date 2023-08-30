# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Quality Control Tier Validation",
    "summary": "Extends the functionality of Quality Control to "
    "support a tier validation process.",
    "version": "15.0.1.0.0",
    "category": "Manufacture",
    "website": "https://github.com/OCA/manufacture",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["mrp", "base_tier_validation"],
    "data": [
        "views/res_config_settings_views.xml",
    ],
    "application": False,
    "installable": True,
}
