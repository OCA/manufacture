# -*- coding: utf-8 -*-
# Copyright 2016  Agile Business Group
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class mrp_repair(models.Model):
    _inherit = 'mrp.repair'

    user_id = fields.Many2one('res.users', 'User',
                              default=lambda self: self.env.user,
                              help="Person in charge for the repair")
    date_repair = fields.Datetime('Repair Date', default=fields.Datetime.now,
                                  copy=False,
                                  help="Date of the repair, this field "
                                  "and user_id defines the calendar")
