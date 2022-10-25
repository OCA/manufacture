# Copyright 2022 Trey, Kilobytes de Soluciones - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Repair Quality Control Issue",
    "version": "12.0.1.0.1",
    "license": "LGPL-3",
    "category": "Quality control",
    "summary": "Add the possibility to create repairs orders from quality "
               "control issues.",
    "author": "Trey, Odoo Community Association (OCA)",
    "maintainers": ["cubells"],
    "website": "https://github.com/OCA/manufacture",
    "depends": ["repair", "quality_control_issue"],
    "data": [
        "wizards/qc_issue_make_repair_views.xml",
        "views/qc_issue_views.xml",
        "views/repair_order_views.xml",
    ],
    "installable": True,
}
