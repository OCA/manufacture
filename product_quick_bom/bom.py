# -*- coding: utf-8 -*-
###############################################################################
#
#   Module for OpenERP
#   Copyright (C) 2015 Akretion (http://www.akretion.com).
#   @author Sébastien BEAU <sebastien.beau@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp import models, fields, api
from collections import defaultdict
from openerp.exceptions import Warning as UserError


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    _sql_constraint = (
        'uniq_product_template',
        'uniq(product_tmpl_id)',
        'You can only have one Bom per product template',
        )


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    product_tmpl_id = fields.Many2one(
        'product.template',
        related='bom_id.product_tmpl_id',
        store=True)
