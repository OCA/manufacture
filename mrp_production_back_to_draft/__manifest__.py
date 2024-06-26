# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "MRP Production Back to Draft",
    "version": "14.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "summary": "Allows to return to draft a confirmed or cancelled MO.",
    "website": "https://github.com/OCA/manufacture",
    "category": "Manufacturing/Manufacturing",
    "license": "AGPL-3",
    "depends": ["mrp"],
    "data": [
        "views/mrp_production_views.xml",
    ],
    "installable": True,
}
