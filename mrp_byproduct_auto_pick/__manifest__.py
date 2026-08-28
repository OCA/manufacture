# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "MRP Byproduct Auto Pick",
    "summary": "Keep manually entered byproduct quantities instead of "
    "resetting them to the quantity to produce",
    "version": "18.0.1.0.0",
    "category": "Manufacturing",
    "license": "AGPL-3",
    "author": "Quartile, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "depends": ["mrp"],
    "data": [
        "views/mrp_production_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "maintainers": ["kanda999", "aungkokolin1997"],
    "installable": True,
}
