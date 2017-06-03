# -*- coding: utf-8 -*-
# © 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "MRP - Partner production notes",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza, "
              "Odoo Community Association (OCA)",
    "website": "http://www.odoomrp.com",
    "contributors": [
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
        "Ana Juaristi <anajuaristi@avanzosc.es>",
        "Bima Wijaya <bimajatiwijaya@gmail.com>",
    ],
    "category": "Tools",
    "depends": [
        "sale",
        "mrp_production_note",
    ],
    "data": [
        "views/res_partner_view.xml",
    ],
    "images": [
        "images/partner_note.png",
    ],
    'installable': True,
}
