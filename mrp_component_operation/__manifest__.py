# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "MRP Components Operations",
    "version": "14.0.1.1.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "summary": "Allows to operate the components from a MO",
    "website": "https://github.com/OCA/manufacture",
    "category": "Manufacturing",
    "depends": ["mrp", "stock_move_forced_lot"],
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_component_operation_views.xml",
        "views/mrp_production_views.xml",
        "views/stock_view.xml",
        "wizards/mrp_component_operate_wizard.xml",
    ],
    "license": "LGPL-3",
    "installable": True,
}
