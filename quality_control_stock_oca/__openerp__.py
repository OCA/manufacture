# -*- coding: utf-8 -*-
# (c) 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# (c) 2014 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Quality control - Stock",
    "version": "8.0.1.0.1",
    "category": "Quality control",
    "license": "AGPL-3",
    "author": "OdooMRP team, "
              "AvanzOSC, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza, "
              "Odoo Community Association (OCA)",
    "website": "http://www.odoomrp.com",
    "contributors": [
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
    ],
    "depends": [
        "quality_control",
        "stock",
    ],
    "data": [
        "data/quality_control_stock_data.xml",
        "views/qc_inspection_view.xml",
        "views/stock_picking_view.xml",
        "views/stock_production_lot_view.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "auto_install": True,
}
