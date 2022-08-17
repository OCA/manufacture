# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Links between subcontracting PO and resupply picking",
    "version": "14.0.1.0.0",
    "category": "Manufacturing",
    "website": "https://github.com/OCA/manufacture",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["mrp_subcontracting", "purchase"],
    "installable": True,
    "data": ["views/stock_picking_view.xml", "views/purchase_order_view.xml"],
    "maintainers": ["victoralmau"],
}
