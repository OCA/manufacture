#  Copyright 2022 Simone Rubino - Takobi
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': "MRP production filter lot",
    'summary': "In production order production popup, "
               "filter lots based on their location and availability",
    'version': '12.0.1.0.1',
    'category': 'Manufacturing',
    'website': "https://github.com/OCA/manufacture"
               "/tree/12.0/mrp_production_filter_lot",
    'author': "Takobi, "
              "Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    'depends': [
        'mrp',
        'stock_picking_filter_lot',
    ],
    'auto_install': True,
    'data': [
        'wizards/mrp_product_produce_views.xml',
    ],
}
