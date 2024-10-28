# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Repair Components Operations",
    "version": "14.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "summary": "Allows to operate the components from a Repair",
    "website": "https://github.com/OCA/manufacture",
    "category": "Manufacturing",
    "depends": ["repair_stock", "stock_move_forced_lot"],
    "data": [
        "security/ir.model.access.csv",
        "views/repair_component_operation_views.xml",
        "views/repair_order_views.xml",
        "views/stock_view.xml",
        "wizards/repair_component_operate_wizard.xml",
    ],
    "license": "LGPL-3",
    "installable": True,
}
