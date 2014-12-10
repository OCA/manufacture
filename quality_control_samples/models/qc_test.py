# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class QcTest(models.Model):
    _inherit = "qc.test"

    sample = fields.Many2one(
        comodel_name="qc.sample", string="Sample definition")
