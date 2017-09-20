# -*- coding: utf-8 -*-
# Copyright (C) 2017 Akretion (http://www.akretion.com). All Rights Reserved
# @author Florian DA COSTA <florian.dacosta@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
import logging
_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.model
    def create(self, values):
        production = super(MrpProduction, self).create(values)
        if production.availability != 'none':
            production.action_assign()
        return production
