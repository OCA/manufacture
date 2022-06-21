# Copyright 2019-21 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "MRP Planned Order Matrix",
    "summary": "Allows to create fixed planned orders on a grid view.",
    "version": "14.0.1.1.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "category": "Warehouse Management",
    "depends": ["mrp_multi_level", "web_widget_x2many_2d_matrix", "date_range"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/mrp_planned_order_wizard_view.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
}
