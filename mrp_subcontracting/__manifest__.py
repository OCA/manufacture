# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "mrp_subcontracting",
    'version': '12.0.1.0.0',
    'summary': "Subcontract Productions",
    'description': "",
    "author": "Odoo S.A., Odoo Community Association (OCA)",
    'website': 'https://www.odoo.com/page/manufacturing',
    'category': 'Manufacturing/Manufacturing',
    'depends': ['mrp'],
    'data': [
        'data/mrp_subcontracting_data.xml',
        'views/mrp_bom_views.xml',
        'views/res_partner_views.xml',
        'views/stock_warehouse_views.xml',
        'views/stock_move_views.xml',
        'views/stock_picking_views.xml',
        'views/supplier_info_views.xml',
    ],
    'demo': [
        'data/mrp_subcontracting_demo.xml',
    ],
}
