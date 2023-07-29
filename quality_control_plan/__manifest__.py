# Copyright 2019 Marcelo Frare (Ass. PNLUG - Gruppo Odoo <http://odoo.pnlug.it>)
# Copyright 2019 Stefano Consolaro (Ass. PNLUG - Gruppo Odoo <http://odoo.pnlug.it>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Quality Control - Control Plan",
    "summary": "Control Plan for Inspection quantity definition.",
    "version": "14.0.1.0.0",
    "author": "Associazione PNLUG - Gruppo Odoo, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "license": "AGPL-3",
    "category": "Quality control",
    "depends": [
        "stock",
        "product",
        "mgmtsystem",
        "mgmtsystem_nonconformity",
        "quality_control_oca",
        "quality_control_stock_oca",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/qc_menu.xml",
        "views/qc_plan_view.xml",
        "views/qc_inspection_view.xml",
        "views/mgmtsystem_nonconformity_view.xml",
        "views/partner_view.xml",
        "views/product_view.xml",
    ],
    "installable": True,
}
