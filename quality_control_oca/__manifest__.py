# -*- coding: utf-8 -*-
# Copyright 2010 NaN Projectes de Programari Lliure, S.L.
# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2014 Oihane Crucelaegui - AvanzOSC
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Quality control",
    "version": "10.0.1.0.3",
    "category": "Quality control",
    "license": "AGPL-3",
    "author": "OdooMRP team, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture/tree/10.0/quality_control",
    "depends": [
        "product",
    ],
    "data": [
        "data/quality_control_data.xml",
        "security/quality_control_security.xml",
        "security/ir.model.access.csv",
        "wizard/qc_test_wizard_view.xml",
        "views/qc_menus.xml",
        "views/qc_inspection_view.xml",
        "views/qc_test_category_view.xml",
        "views/qc_test_view.xml",
        "views/qc_trigger_view.xml",
        "views/product_template_view.xml",
        "views/product_category_view.xml",
    ],
    "demo": [
        "demo/quality_control_demo.xml",
    ],
    "installable": True,
}
