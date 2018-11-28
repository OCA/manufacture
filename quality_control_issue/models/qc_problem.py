# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Aleph Objects, Inc. (https://www.alephobjects.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, SUPERUSER_ID

AVAILABLE_PRIORITIES = [
    ('0', 'Normal'),
    ('1', 'Low'),
    ('2', 'High'),
    ('3', 'Very High'),
]


class QcProblem(models.Model):
    _name = "qc.problem"
    _description = "Quality Control Problem Tracking"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_default_stage_id(self):
        """ Gives default stage_id """
        team = self.env['qc.team']._get_default_qc_team_id(
            user_id=self.env.uid)
        return self.stage_find([], team, [('fold', '=', False)])

    @api.multi
    def _read_group_stage_ids(self, stages, domain, order=None):
        search_domain = []
        qc_team_id = self.env.context.get('default_qc_team_id') or False
        if qc_team_id:
            search_domain += ['|', ('id', 'in', stages.ids)]
            search_domain += ['|', ('qc_team_id', '=', qc_team_id)]
            search_domain += [('qc_team_id', '=', False)]
        else:
            search_domain += ['|', ('id', 'in', stages.ids)]
            search_domain += [('qc_team_id', '=', False)]

        stage_ids = stages._search(
            search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    @api.one
    @api.depends('issue_ids')
    def _compute_count(self):
        self.issue_count = len(self.issue_ids)

    name = fields.Char()
    notes = fields.Text()
    issue_ids = fields.Many2many(
        comodel_name="qc.issue", string="QC Issues",
        relation="qc_issue_problem_rel", column1="qc_problem_id",
        column2="qc_issue_id")
    problem_group_id = fields.Many2one(
        comodel_name="qc.problem.group", string="Problem Group")
    issue_count = fields.Integer(
        string="Issues", compute=_compute_count, store=True)
    color = fields.Integer(string='Color Index')
    priority = fields.Selection(
        selection=AVAILABLE_PRIORITIES, string='Rating', index=True)
    stage_id = fields.Many2one(
        comodel_name="qc.stage", string='Stage',
        track_visibility='onchange',
        index=True, default=_get_default_stage_id,
        group_expand='_read_group_stage_ids',
        domain="['|', ('qc_team_id', '=', False), "
               "('qc_team_id', '=', qc_team_id)]",
    )
    qc_team_id = fields.Many2one(
        comodel_name='qc.team', string='QC Team',
        default=lambda self: self.env[
            'qc.team'].sudo()._get_default_qc_team_id(user_id=self.env.uid),
        index=True, track_visibility='onchange')
    company_id = fields.Many2one(
        comodel_name='res.company', string='Company', required=True,
        default=lambda self: self.env.user.company_id)
    _group_by_full = {
        'stage_id': _read_group_stage_ids
    }

    def stage_find(self, cases, team, domain=None, order='sequence'):
        """ Override of the base.stage method
            Parameter of the stage search taken from the problem:
            - team_id: if set, stages must belong to this team or
              be a default stage; if not set, stages must be default
              stages
        """
        team_ids = set()
        if team:
            team_ids.add(team.id)
        for problem in cases:
            if problem.team_id:
                team_ids.add(problem.team_id.id)
        search_domain = []
        if team_ids:
            search_domain += [('|')] * (len(team_ids))
            search_domain.append(('qc_team_id', '=', False))
            for team_id in team_ids:
                search_domain.append(('qc_team_id', '=', team_id))
        else:
            search_domain.append(('qc_team_id', '=', False))
        search_domain += list(domain)
        # perform search, return the first found
        stage = self.env['qc.stage'].search(
            search_domain, order=order, limit=1)
        return stage
