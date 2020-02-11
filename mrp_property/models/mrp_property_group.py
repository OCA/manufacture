# coding: utf-8
# Copyright 2008 - 2016 Odoo S.A.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import fields, models


class MrpPropertyGroup(models.Model):
    """ Group of mrp properties """
    _name = 'mrp.property.group'
    _description = 'Property Group'

    name = fields.Char(required=True)
    description = fields.Text()
