
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2008-2014 AvanzOSC (Daniel). All Rights Reserved
#    Date: 10/07/2014
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import models, fields


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    pre_op_product = fields.Many2one('product.product',
                                     string='Pre Operation Cost')
    post_op_product = fields.Many2one('product.product',
                                      string='Post Operation Cost')
    rt_operations = fields.Many2many(
        'mrp.routing.operation', 'mrp_operation_workcenter_rel', 'workcenter',
        'operation', 'Routing Operations')
