# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Mrp Bom Responsible",
    "summary": """
        Adds a responsible to the Bill of Materials which then will be
        forwarded to the Manufacturing Order""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ForgeFlow S.L., Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "depends": ["mrp"],
    "data": [
        "views/mrp_bom_views.xml",
    ],
}
