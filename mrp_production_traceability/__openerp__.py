# -*- coding: utf-8 -*-
# Copyright (c)
#    2015 Serv. Tec. Avanzados - Pedro M. Baeza (http://www.serviciosbaeza.com)
#    2015 AvanzOsc (http://www.avanzosc.es)
# Copyright 2017 Lorenzo Battistini - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "MRP Production Traceability",
    "version": "8.0.1.0.0",
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "website": "http://www.odoomrp.com",
    "category": "Manufacturing",
    "depends": [
        "mrp",
        "stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_production_view.xml",
        "views/track_lot_view.xml",
        "views/stock_move_view.xml",
        "wizard/open_lots_tree_view.xml",
    ],
    "installable": True,
}
