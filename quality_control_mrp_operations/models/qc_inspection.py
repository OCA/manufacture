# -*- coding: utf-8 -*-
# (c) 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields


class QcInspection(models.Model):
    _inherit = 'qc.inspection'

    workcenter_line_id = fields.Many2one(
        'mrp.production.workcenter.line', string='Operation', index=True)


class QcInspectionLine(models.Model):
    _inherit = 'qc.inspection.line'

    workcenter_line_id = fields.Many2one(
        comodel_name="mrp.production.workcenter.line",
        related="inspection_id.workcenter_line_id",
        store=True, string="Operation")
