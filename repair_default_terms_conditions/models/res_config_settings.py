# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    default_quotation_notes = fields.Text(
        related='company_id.repair_note',
        string="Repair Terms & Conditions",
        default_model="repair.order",
        readonly=False)

    use_repair_note = fields.Boolean(
        string='Use Repair Default Terms & Conditions',
        config_parameter='repair.use_repair_note')
