# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
import openerp.addons.decimal_precision as dp


class QualityControlIssue(models.Model):
    _name = "qc.issue"
    _description = "Quality Control Issue"
    _inherit = "mail.thread"

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'qc.issue') or ''
        return super(QualityControlIssue, self).create(vals)

    @api.one
    def _get_uom(self):
        self.product_uom = self.product_id.product_tmpl_id.uom_id

    def _get_default_stage_id(self):
        """ Gives default stage_id """
        team_id = self.env['qc.team']._get_default_qc_team_id(
            user_id=self.env.uid)
        return self.issue_stage_find([], team_id, [('fold', '=', False)])

    @api.multi
    def _read_group_stage_ids(self, domain, read_group_order=None,
                              access_rights_uid=None):
        access_rights_uid = access_rights_uid or self._uid
        stage_obj = self.env['qc.issue.stage']
        search_domain = []
        qc_team_id = self.env.context.get('default_qc_team_id') or False
        if qc_team_id:
            search_domain += ['|', ('id', 'in', self.ids)]
            search_domain += ['|', ('qc_team_id', '=', qc_team_id)]
            search_domain += [('qc_team_id', '=', False)]
        else:
            search_domain += ['|', ('id', 'in', self.ids)]
            search_domain += [('qc_team_id', '=', False)]
        # perform search
        stage_ids = stage_obj._search(search_domain,
                                      access_rights_uid=access_rights_uid)
        result = [stage.name_get()[0] for stage in
                  stage_obj.browse(stage_ids)]
        # restore order of the search
        result.sort(
            lambda x, y: cmp(stage_ids.index(x[0]), stage_ids.index(y[0])))

        fold = {}
        for stage in stage_obj.browse(stage_ids):
            fold[stage.id] = stage.fold or False
        return result, fold

    name = fields.Char(readonly=True)
    state = fields.Selection(
        selection=[("new", "New"),
                   ("progress", "In Progress"),
                   ("done", "Done"),
                   ("cancel", "Cancel")], default="new",
        track_visibility='onchange')
    product_id = fields.Many2one(
        comodel_name="product.product", string="Product",
        readonly=True, states={"new": [("readonly", False)]},
        required=True)
    product_tracking = fields.Selection(related="product_id.tracking")
    product_qty = fields.Float(
        string="Product Quantity", required=True, default=1.0,
        readonly=True, states={"new": [("readonly", False)]},
        digits_compute=dp.get_precision("Product Unit of Measure"))
    product_uom = fields.Many2one(
        comodel_name="product.uom", string="Product Unit of Measure",
        required=True, default=_get_uom,
        readonly=True, states={"new": [("readonly", False)]},)
    lot_id = fields.Many2one(
        comodel_name="stock.production.lot", string="Lot/Serial Number",
        readonly=True, states={"new": [("readonly", False)]},)
    location_id = fields.Many2one(
        comodel_name="stock.location", string="Location",
        readonly=True, states={"new": [("readonly", False)]},)
    inspector_id = fields.Many2one(
        comodel_name="res.users", string="Inspector",
        track_visibility="onchange",
        readonly=True, states={"new": [("readonly", False)]},
        default=lambda self: self.env.user, required=True)
    responsible_id = fields.Many2one(
        comodel_name="res.users", string="Assigned to",
        track_visibility="onchange",
        states={"done": [("readonly", True)]},)
    description = fields.Text(
        states={"done": [("readonly", True)]},)
    qc_problem_ids = fields.Many2many(
        comodel_name="qc.problem", string="Problems",
        relation="qc_issue_problem_rel", column1="qc_issue_id",
        column2="qc_problem_id",
        states={"done": [("readonly", True)]},)
    color = fields.Integer(string='Color Index')
    stage_id = fields.Many2one(
        comodel_name="qc.issue.stage", string='Stage',
        track_visibility='onchange',
        select=True, default=_get_default_stage_id,
        domain="['|', ('qc_team_id', '=', False), "
               "('qc_team_id', '=', qc_team_id)]")
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

    def issue_stage_find(self, cases, team_id, domain=None, order='sequence'):
        """ Override of the base.stage method
            Parameter of the stage search taken from the problem:
            - team_id: if set, stages must belong to this team or
              be a default stage; if not set, stages must be default
              stages
        """
        team_ids = set()
        if team_id:
            team_ids.add(team_id)
        for problem in cases:
            if problem.team_id:
                team_ids.add(problem.team_id.id)
        search_domain = []
        if team_ids:
            search_domain += [('|')] * (len(team_ids) - 1)
            for team_id in team_ids:
                search_domain.append(('qc_team_id', '=', team_id.id))
        search_domain += list(domain)
        # perform search, return the first found
        stage_ids = self.env['qc.issue.stage'].search(
            search_domain, order=order, limit=1)
        if stage_ids:
            return stage_ids[0]
        return False

    @api.multi
    def action_confirm(self):
        self.write({'state': 'progress'})

    @api.multi
    def action_done(self):
        self.write({'state': 'done'})

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.product_uom = self.product_id.product_tmpl_id.uom_id
        if self.lot_id.product_id != self.product_id:
            self.lot_id = False
        if self.product_id:
            return {'domain': {
                'lot_id': [('product_id', '=', self.product_id.id)]}}
        return {'domain': {'lot_id': []}}

    @api.onchange("lot_id")
    def _onchange_lot_id(self):
        product = self.lot_id.product_id
        if product:
            self.product_id = product
            self.product_uom = product.product_tmpl_id.uom_id
