# -*- coding: utf-8 -*-
# (c) 2016 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Procurement Service",
    "version": "10.0.1.0.0",
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza,"
              "Odoo Community Association (OCA)",
    "website": "http://www.odoomrp.com",
    "license": "AGPL-3",
    "category": "Procurements",
    "depends": [
        "product",
        "sale",
        "stock",
        "purchase",
        "sale_stock",
    ],
    "data": [
        "views/product_template_view.xml",
    ],
    "installable": True
}
