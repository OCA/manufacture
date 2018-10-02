# -*- coding: utf-8 -*-
# (c) 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Quality Control - MRP Operations',
    'version': '8.0.1.0.0',
    'summary': 'Enables quality control for MRP operations',
    'author': 'Serv. Tec. Avanzados,Odoo Community Association (OCA)',
    'website': 'http://www.odoomrp.com',
    'category': 'Quality control',
    'depends': [
        'mrp_operations_extension',
        'quality_control',
    ],
    'data': [
        'views/qc_inspection_view.xml',
        'views/mrp_routing_operation_view.xml',
        'views/mrp_production_workcenter_line_view.xml',
    ],
    'installable': True,
    'license': 'AGPL-3',
}
