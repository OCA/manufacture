# -*- coding: utf-8 -*-
# Copyright 2010 NaN Projectes de Programari Lliure, S.L.
# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2014 Oihane Crucelaegui - AvanzOSC
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class QcInspectionSetTest(models.TransientModel):
    """This wizard is used to preset the test for a given
    inspection. This will not only fill in the 'test' field, but will
    also fill in all lines of the inspection with the corresponding lines of
    the template.
    """
    _name = 'qc.inspection.set.test'

    test = fields.Many2one(comodel_name='qc.test', string='Test')

    @api.multi
    def action_create_test(self):
        inspection = self.env['qc.inspection'].browse(
            self.env.context['active_id'])
        inspection.test = self.test
        inspection.inspection_lines.unlink()
        inspection.inspection_lines = inspection._prepare_inspection_lines(
            self.test)
        return True
