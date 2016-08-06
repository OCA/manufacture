# -*- coding: utf-8 -*-
# © 2015 Daniel Campos
# © 2015 Pedro M. Baeza
# © 2015 Ana Juaristi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "MRP Operations start without material",
    "version": "8.0.1.0.1",
    "author": "Tecnativa,"
              "AvanzOSC,"
              "OdooMRP Team,"
              "Odoo Community Association (OCA)",
    "website": "http://www.odoomrp.com",
    "depends": ["mrp_operations_extension"],
    "category": "Manufacturing",
    "data": ['views/mrp_routing_view.xml',
             'views/mrp_production_view.xml'
             ],
    "installable": True,
    "application": True
}
