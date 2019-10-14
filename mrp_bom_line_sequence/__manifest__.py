# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'BOM lines with sequence number',
    'summary': 'Manages the order of BOM lines by displaying its sequence',
    'version': '12.0.1.0.0',
    'category': 'Manufacturing Management',
    'author': "Eficent, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/manufacture',
    'license': "AGPL-3",
    'depends': ['mrp'],
    'data': ['views/stock_view.xml'],
    'installable': True,
}
