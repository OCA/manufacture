# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
# Copyright 2019 Odoo
# Copyright 2020 Tecnativa - Alexandre Díaz
# Copyright 2020 Tecnativa - Pedro M. Baeza

{
    'name': "Subcontract Productions",
    'version': '12.0.1.0.1',
    "author": "Odoo S.A., Tecnativa, Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/manufacture',
    'category': 'Manufacturing Orders & BOMs',
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
    "uninstall_hook": "uninstall_hook",
    "license": "LGPL-3",
}
