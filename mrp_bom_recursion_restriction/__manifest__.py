# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "MRP BoM Recursion Restriction",
    "version": "14.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "maintainers": ["ChrisOForgeFlow"],
    "summary": "Logs any change to a BoM in the chatter.",
    "website": "https://github.com/OCA/manufacture",
    "category": "Manufacturing",
    "depends": ["mrp"],
    "data": [
        "views/mrp_bom_view.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
    "development_status": "Alpha",
}
