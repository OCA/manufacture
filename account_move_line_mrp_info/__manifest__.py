# © 2022ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Account Move Line Mrp Info",
    "version": "14.0.1.1.0",
    "author": "ForgeFlow," "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "category": "Manufacture",
    "depends": ["account_move_line_stock_info", "mrp"],
    "installable": True,
    "pre_init_hook": "pre_init_hook",
    "license": "AGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "views/account_move_line_view.xml",
        "views/mrp_production_view.xml",
    ],
}
