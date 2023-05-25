# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "MRP Component Operation Scrap Reason",
    "version": "14.0.1.1.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "summary": "Allows to pass a reason to scrap with MRP component operation",
    "website": "https://github.com/OCA/manufacture",
    "category": "Manufacturing/Manufacturing",
    "license": "AGPL-3",
    "depends": ["scrap_reason_code", "mrp_component_operation"],
    "data": [
        "wizards/mrp_component_operate_wizard.xml",
    ],
    "installable": True,
    "auto_install": True,
}
