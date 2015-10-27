# -*- coding: utf-8 -*-
##########################################################################
#                                                                        #
# Copyright 2015  Lorenzo Battistini - Agile Business Group              #
# About license, see __openerp__.py                                      #
#                                                                        #
##########################################################################

from openerp import models, fields


class MrpRepairLayoutCategory(models.Model):
    _name = 'mrp_repair.layout.category'
    name = fields.Char('Name', required=True)
    sequence = fields.Integer('Sequence', required=True, default=10)
    subtotal = fields.Boolean('Add subtotal', default=True)
    separator = fields.Boolean('Add separator', default=True)
    pagebreak = fields.Boolean('Add pagebreak')
