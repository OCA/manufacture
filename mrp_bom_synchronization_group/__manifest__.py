# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "MRP BoM Synchronization Group",
    "summary": "Group Bills of Materials to keep their components synchronized",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "category": "Manufacturing",
    "depends": ["mrp"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/mrp_bom_synchronization_wizard_views.xml",
        "views/mrp_bom_synchronization_group_views.xml",
        "views/mrp_bom_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
}
