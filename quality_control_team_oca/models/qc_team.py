# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class QualityControlTeam(models.Model):
    _name = "qc.team"
    _inherit = ['mail.thread']
    _description = "Quality Control Team"
    _order = "name"

    @api.model
    def _get_default_qc_team_id(self, user_id=None):
        if not user_id:
            user_id = self.env.uid
        qc_team_id = None
        if 'default_qc_team_id' in self.env.context:
            qc_team_id = self.env['qc.team'].browse(
                self.env.context.get('default_qc_team_id'))
        if not qc_team_id or not qc_team_id.exists():
            company_id = self.sudo(user_id).company_id.id
            qc_team_id = self.env['qc.team'].sudo().search([
                '|',
                ('user_id', '=', user_id),
                ('member_ids', '=', user_id),
                '|',
                ('company_id', '=', False),
                ('company_id', 'child_of', [company_id])
            ], limit=1)
        if not qc_team_id:
            default_team_id = self.env.ref(
                'quality_control_team.qc_team_main', raise_if_not_found=False)
            if default_team_id:
                qc_team_id = default_team_id
        return qc_team_id

    name = fields.Char(
        string='Quality Control Team', required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        comodel_name='res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get(
            'qc.team'))
    user_id = fields.Many2one(
        comodel_name='res.users', string='Team Leader')
    member_ids = fields.One2many(
        comodel_name='res.users', inverse_name='qc_team_id',
        string='Team Members')
    reply_to = fields.Char(
        string='Reply-To',
        help="The email address put in the 'Reply-To' of all emails sent by "
             "Odoo about cases in this QC team")
    color = fields.Integer(string='Color Index', help="The color of the team")

    @api.model
    def create(self, values):
        return super(
            QualityControlTeam,
            self.with_context(mail_create_nosubscribe=True)).create(values)
