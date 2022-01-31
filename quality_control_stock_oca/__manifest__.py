# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2014 Oihane Crucelaegui - AvanzOSC
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Quality control - Stock (OCA)",
    "version": "14.0.1.0.0",
    "category": "Quality control",
    "license": "AGPL-3",
    "author": "OdooMRP team, AvanzOSC, Serv. Tecnol. Avanzados - Pedro M. Baeza, "
    "Agile Business Group, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/manufacture",
    "depends": ["quality_control_oca", "stock"],
    "data": [
        "views/qc_inspection_view.xml",
        "views/stock_picking_view.xml",
        "views/stock_production_lot_view.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "auto_install": True,
}
