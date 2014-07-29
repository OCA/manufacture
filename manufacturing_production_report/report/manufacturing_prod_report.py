# -*- encoding: utf-8 -*-
# #############################################################################
#
# OpenERP, Open Source Management Solution
# This module copyright (C) 2010 - 2014 Savoir-faire Linux
# (<http://www.savoirfairelinux.com>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# #############################################################################

from openerp.osv import fields, orm
from openerp import tools
from openerp.tools.translate import _

MONTHS = [('01', 'January'), ('02', 'February'), ('03', 'March'),
          ('04', 'April'), ('05', 'May'), ('06', 'June'),
          ('07', 'July'), ('08', 'August'), ('09', 'September'),
          ('10', 'October'), ('11', 'November'), ('12', 'December')]


class production_analysis_report(orm.Model):
    _name = 'production_analysis.report'
    _description = 'Production Analysis report'
    _auto = False
    _columns = {
        'product_id': fields.many2one('product.product', 'Product',
                                      readonly=True),
        "product_qty": fields.float("Quantity", readonly=True),
        "product_category_id": fields.many2one('product.category',
                                               'Category of product',
                                               readonly=True),
        "serial_number": fields.char("Serial Number",
                                     readonly=True),
        "routing_name": fields.char("Machine", readonly=True),
        'date': fields.date('Date', readonly=True, help='Date'),
        'creation_day': fields.char('Day', size=10, readonly=True),
        'creation_week': fields.char('Week', size=10, readonly=True),
        'creation_month': fields.selection(
            [('01', 'January'), ('02', 'February'), ('03', 'March'),
             ('04', 'April'), ('05', 'May'), ('06', 'June'),
             ('07', 'July'), ('08', 'August'), ('09', 'September'),
             ('10', 'October'), ('11', 'November'), ('12', 'December')],
            'Month', readonly=True),
        'creation_year': fields.char('Year', size=10, readonly=True),
        'production_id': fields.many2one('mrp.production',
                                         'Production',
                                         readonly=True),
        'user_id': fields.many2one('res.users',
                                   'Responsible',
                                   readonly=True),
    }

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'production_analysis_report')
        cr.execute("""
            CREATE OR REPLACE VIEW production_analysis_report AS (
                SELECT
                    min(s.id) AS id,
                    p.product_id AS product_id,
                    p.product_qty AS product_qty,
                    prt.categ_id as product_category_id,
                    spl.name AS serial_number,
                    r.name AS routing_name,
                    to_date(to_char(s.date, 'YYYY-MM-DD'),'YYYY-MM-DD') AS date,
                    to_char(s.date, 'YYYY-MM-DD') as creation_day,
                    to_char(s.date, 'MM') as creation_month,
                    to_char(s.date, 'YYYY') as creation_year,
                    extract(week from s.date) as creation_week,
                    s.production_id as production_id,
                    p.user_id AS user_id

                FROM stock_move s
                    RIGHT JOIN mrp_production p ON (s.production_id = p.id)
                    LEFT JOIN product_product pr ON (s.product_id = pr.id)
                    LEFT JOIN product_template prt ON (s.product_id = prt.id)
                    LEFT JOIN mrp_routing r ON (p.routing_id = r.id)
                    LEFT JOIN stock_production_lot spl ON (s.prodlot_id = spl.id)

                WHERE
                    s.state = 'done'

                GROUP BY
                    s.date,
                    p.product_id,
                    p.product_qty,
                    prt.categ_id,
                    spl.name,
                    r.name,
                    s.production_id,
                    p.user_id
            )
        """)

    def unlink(self, cr, uid, ids, context=None):
        raise orm.except_orm(_('Error!'), _('You cannot delete any record!'))
