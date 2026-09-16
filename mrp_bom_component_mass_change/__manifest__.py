# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "MRP BoM Component Mass Change",
    "version": "17.0.1.1.0",
    "category": "Manufacturing",
    "summary": "Replace or remove a component in several BoMs at once",
    "website": "https://github.com/OCA/manufacture",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["mrp"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/mrp_bom_component_mass_change_views.xml",
        "views/mrp_bom_views.xml",
    ],
}
