# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2014 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "MRP extension for quality control (OCA)",
    "version": "17.0.1.1.0",
    "category": "Quality control",
    "license": "AGPL-3",
    "author": "OdooMRP team, "
    "AvanzOSC, "
    "Serv. Tecnol. Avanzados - Pedro M. Baeza, "
    "Agile Business Group, "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "depends": ["quality_control_oca", "quality_control_stock_oca", "mrp"],
    "data": [
        "data/quality_control_mrp_data.xml",
        "views/qc_inspection_view.xml",
        "views/mrp_production_view.xml",
    ],
    "installable": True,
    "auto_install": True,
}
