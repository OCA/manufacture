# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": "Stock moves of manufacturing orders added to unbuild orders",
    "version": "14.0.1.0.0",
    "license": "LGPL-3",
    "category": "Manufacture",
    "summary": "Link the stock moves of manufacturing orders to the respective unbuild orders",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "depends": ["mrp_account"],
    "data": ["views/stock_move_views.xml"],
    "installable": True,
}
