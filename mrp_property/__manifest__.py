# coding: utf-8
# Copyright 2008-2016 Odoo S.A.
# Copyright 2018 Opener B.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    'name': "MRP Properties on Sale Order Lines",
    'summary': 'Control BoM selection from properties on sale order lines',
    'version': '10.0.1.0.0',
    'category': 'Manufacturing',
    'author': "Odoo S.A.,Opener B.V.,Odoo Community Association (OCA)",
    'development_status': 'stable',
    'website': 'https://github.com/oca/manufacture',
    'license': 'LGPL-3',
    'depends': [
        'sale_mrp',
    ],
    'data': [
        'views/mrp_bom.xml',
        'views/mrp_property.xml',
        'views/mrp_property_group.xml',
        'views/procurement_order.xml',
        'views/sale_order.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'post_init_hook': 'post_init_hook',
}
