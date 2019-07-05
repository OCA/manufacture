# Copyright 2016 Ucamco - Wim Audenaert <wim.audenaert@ucamco.com>
# Copyright 2016-19 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'MRP Multi Level',
    'version': '11.0.3.1.0',
    'development_status': 'Beta',
    'license': 'AGPL-3',
    'author': 'Ucamco, '
              'Eficent, '
              'Odoo Community Association (OCA)',
    'maintainers': ['jbeficent', 'lreficent'],
    'summary': 'Adds an MRP Scheduler',
    'website': 'https://github.com/OCA/manufacture',
    'category': 'Manufacturing',
    'depends': [
        'mrp',
        'stock',
        'purchase',
        'stock_demand_estimate',
        'mrp_warehouse_calendar',
    ],
    'data': [
        'security/mrp_multi_level_security.xml',
        'security/ir.model.access.csv',
        'views/mrp_area_views.xml',
        'views/product_product_views.xml',
        'views/product_template_views.xml',
        'views/product_mrp_area_views.xml',
        'views/stock_location_views.xml',
        'wizards/mrp_inventory_procure_views.xml',
        'views/mrp_inventory_views.xml',
        'wizards/mrp_multi_level_views.xml',
        'views/mrp_menuitem.xml',
        'data/mrp_multi_level_cron.xml',
        'data/mrp_area_data.xml',
    ],
    'demo': [
        'demo/product_category_demo.xml',
        'demo/product_product_demo.xml',
        'demo/res_partner_demo.xml',
        'demo/product_supplierinfo_demo.xml',
        'demo/product_mrp_area_demo.xml',
        'demo/mrp_bom_demo.xml',
        'demo/initial_on_hand_demo.xml',
    ],
    'installable': True,
    'application': True,
}
