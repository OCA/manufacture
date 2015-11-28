# -*- coding: utf-8 -*-
# (c) 2015 Eficent - Jordi Ballester Alomar
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'mrp_production_order_analytic',
    'summary': 'Adds the analytic account to the production order',
    'version': '8.0.1.0.0',
    'category': "Manufacturing",
    'author': 'Eficent, '
              'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'depends': ['mrp', 'analytic'],
    'data': [
        "views/mrp_view.xml",
        "views/analytic_account_view.xml",
    ],
    'installable': True,
}
