# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2015 Alessio Gerace- Agile Business Group
#
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#
##############################################################################

{
    "name": "Web Digitized Signature for mrp repair",
    "version": "8.0.1.0.0",
    "author": "Agile Business Group, "
               "Odoo Community Association (OCA)",
    "category": 'Manufacturing',
    "license": "AGPL-3",
    'depends': ['web_widget_digitized_signature', 'mrp_repair'],
    'data': [
        'views/mrp_repair_view.xml'
    ],
    'website': 'http://www.agilebg.com',
    'installable': True,
    'auto_install': False,
}
