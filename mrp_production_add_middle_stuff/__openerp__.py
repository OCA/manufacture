# -*- coding: utf-8 -*-
# (c) 2015 Pedro M. Baeza - Serv. Tecnol. Avanzados
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'MRP Production add middle stuff',
    'version': "1.0",
    "category": "Manufacturing",
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    'contributors': ["Daniel Campos <danielcampos@avanzosc.es>",
                     "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
                     "Ana Juaristi <ajuaristio@gmail.com>"],
    'website': "http://www.odoomrp.com",
    'depends': ["mrp"],
    'data': ["wizard/addition_wizard_view.xml",
             "views/mrp_production_view.xml"],
    'installable': True,
}
