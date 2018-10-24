# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Aleph Objects, Inc. (https://www.alephobjects.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

AVAILABLE_PRIORITIES = [
    ('0', 'Normal'),
    ('1', 'Low'),
    ('2', 'High'),
    ('3', 'Very High'),
]


class QualityControlIssueStage(models.Model):
    _name = "qc.issue.stage"
    _rec_name = 'name'
    _order = "sequence, name, id"

    @api.model
    def default_get(self, fields):
        """ Hack :  when going from the kanban view, creating a stage with a
        qc team in context should not create a stage for the current team only.
        """
        ctx = dict(self.env.context)
        if ctx.get('default_qc_team_id') and not ctx.get('some_context'):
            ctx.pop('default_qc_team_id')
        return super(QualityControlIssueStage,
                     self.with_context(ctx)).default_get(fields)

    name = fields.Char('Stage Name', required=True)
    sequence = fields.Integer(
        string='Sequence', help="Used to order stages. Lower is better.",
        default=1)
    qc_team_id = fields.Many2one(
        comodel_name='qc.team', string='Quality Control Team',
        ondelete='set null')
    fold = fields.Boolean(
        string='Folded in Pipeline', default=False,
        help='This stage is folded in the kanban view when there are no '
             'records in that stage to display.')
    state = fields.Selection(
        string="QC State",
        selection=lambda self: self.env['qc.issue']._fields['state'].selection)
