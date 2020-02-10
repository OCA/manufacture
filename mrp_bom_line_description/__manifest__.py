# Copyright 2020 PlanetaTIC <info@planetatic.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'BoM line description',
    'summary': 'Description on BoM lines',
    'version': '12.0.1.0.0',
    'development_status': 'Beta',
    'category': 'Manufacturing',
    'website': 'https://github.com/OCA/manufacture',
    'author': 'PlanetaTIC, '
              'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'mrp',
    ],
    'data': [
        'views/mrp_bom_views.xml',
        'report/mrp_report_bom_structure.xml',
    ],
}
