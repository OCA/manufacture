# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

{
    "name": "Production By-Product Cost Share",
    "version": "14.0.1.0.0",
    "category": "MRP",
    "author": "ForgeFlow, Odoo Community Association (OCA), Odoo S.A.",
    "website": "https://github.com/OCA/manufacture",
    "license": "LGPL-3",
    "depends": ["mrp", "mrp_account"],
    "data": [
        "views/mrp_production_views.xml",
        "views/mrp_bom_views.xml",
        "views/mrp_template.xml",
        "report/mrp_report_bom_structure.xml",
    ],
    "installable": True,
}
