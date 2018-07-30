# -*- coding: utf-8 -*-
# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2014 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "MRP extension for quality control",
    "version": "10.0.1.0.0",
    "category": "Quality control",
    "license": "AGPL-3",
    "author": "OdooMRP team, "
              "AvanzOSC, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza, "
              "Agile Business Group, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture/tree/10.0/"
               "quality_control_mrp",
    "depends": [
        "quality_control",
        "quality_control_stock",
        "mrp"
    ],
    "data": [
        'data/quality_control_mrp_data.xml',
        'views/qc_inspection_view.xml',
        'views/mrp_production_view.xml',
    ],
    "installable": True,
    "auto_install": True,
}
