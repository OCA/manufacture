# -*- coding: utf-8 -*-
##########################################################################
#                                                                        #
# Copyright 2015  Lorenzo Battistini - Agile Business Group              #
# About license, see __openerp__.py                                      #
#                                                                        #
##########################################################################

from openerp import models, fields, api
from itertools import groupby


class MrpRepair(models.Model):
    _inherit = 'mrp.repair'

    @api.model
    def grouplines(self, ordered_lines, sortkey):
        """Return lines from a specified invoice or sale order grouped by
        category"""
        grouped_lines = []
        for key, valuesiter in groupby(ordered_lines, sortkey):
            group = {}
            group['category'] = key
            group['lines'] = list(v for v in valuesiter)

            if 'subtotal' in key and key.subtotal is True:
                group['subtotal'] = sum(
                    line.price_subtotal for line in group['lines'])
            grouped_lines.append(group)

        return grouped_lines

    @api.model
    def repair_layout_operation_lines(self, order):
        ordered_lines = order.operations

        def sortkey(x):
            return x.layout_cat_id if x.layout_cat_id else ''

        return self.grouplines(ordered_lines, sortkey)


class MrpRepairLine(models.Model):
    _inherit = 'mrp.repair.line'
    _order = 'repair_id, categ_sequence, layout_cat_id, id'
    layout_cat_id = fields.Many2one(
        'mrp_repair.layout.category', 'Section')
    categ_sequence = fields.Integer(
        related='layout_cat_id.sequence', string='Layout sequence',
        store=True, default=0)
