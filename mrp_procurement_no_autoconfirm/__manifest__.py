# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "MRP - Prevent MO confirmed when comes from a parent MO",
    "summary": "For child MOs, prevent auto confirmation",
    "version": "18.0.1.0.0",
    "category": "Manufacturing",
    "website": "https://github.com/OCA/manufacture",
    "author": "Solvos, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["mrp"],
    "data": [
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
}
