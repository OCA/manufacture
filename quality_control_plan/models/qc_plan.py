# Copyright 2019 Marcelo Frare (Ass. PNLUG - Gruppo Odoo <http://odoo.pnlug.it>)
# Copyright 2019 Stefano Consolaro (Ass. PNLUG - Gruppo Odoo <http://odoo.pnlug.it>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class QcPlan(models.Model):
    """
    New model
    to manage quality control plans
    """

    # model
    _name = 'qc.plan'
    _description = 'Quality Control Plan'

    # extend model of messages and followers
    _inherit = ['mail.thread']

    # fields
    # name: alphanumeric id
    name = fields.Char('Name', required=True)
    # description of plan calculation
    description = fields.Char('Description')
    # free pass option
    free_pass = fields.Boolean('Free pass')
    # control levels of the plan
    plan_ids = fields.One2many('qc.level', 'plan_id', 'Plan')

    @api.onchange('free_pass')
    def on_change_free_pass(self):
        """
        Check if there is only one free pass plan
        set the last changed to false if another exists
        """

        if self.free_pass:
            if self.env['qc.plan'].search([('free_pass', '=', True)]):
                self.free_pass = False
                raise models.ValidationError_('A free pass plan already exists.')


class QcLevel(models.Model):
    """
    New model
    to manage the lelevs for a control plan
    """

    # model
    _name = 'qc.level'
    _description = 'Quality Control Plan Levels'

    # fields
    # plan reference
    plan_id = fields.Many2one('qc.plan', 'Plan', required=True)
    # minimum quantity ingoing
    qty_received = fields.Float('Quantity to inspect')
    # quantity value to check
    qty_checked = fields.Float('Quantity checked')
    # chek value type: absolute or percent of ingoing quantity
    chk_type = fields.Selection([('nr', 'Absolute value'),
                                 ('percent', 'Percent'),
                                 ],
                                'Measure',
                                default='nr')

    # define record name to display in form view
    _rec_name = 'id'
