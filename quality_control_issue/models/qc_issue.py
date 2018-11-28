# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Aleph Objects, Inc. (https://www.alephobjects.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp


class QualityControlIssue(models.Model):
    _name = "qc.issue"
    _description = "Quality Control Issue"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.multi
    def _compute_stock_scrap_qty(self):
        for rec in self:
            rec.stock_scrap_qty = sum(
                self.stock_scrap_ids.mapped('scrap_qty'))

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
        team = self.env['qc.team']._get_default_qc_team_id(
            user_id=self.env.uid)
        return self.issue_stage_find([], team, [('fold', '=', False)])

    def _get_default_location_id(self):
        company_user = self.env.user.company_id
        warehouse = self.env['stock.warehouse'].search([
            ('company_id', '=', company_user.id)], limit=1)
        if warehouse:
            return warehouse.lot_stock_id.id
        return None

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

    name = fields.Char(readonly=True)
    state = fields.Selection(
        selection=[("new", "New"),
                   ("progress", "In Progress"),
                   ("done", "Done"),
                   ("cancel", "Cancel")], default="new",
        track_visibility='onchange', readonly=True)
    product_id = fields.Many2one(
        comodel_name="product.product", string="Product",
        readonly=True, states={"new": [("readonly", False)]}, required=True)
    product_tracking = fields.Selection(related="product_id.tracking")
    product_qty = fields.Float(
        string="Product Quantity", required=True, default=1.0,
        readonly=True, states={"new": [("readonly", False)]},
        digits=dp.get_precision("Product Unit of Measure"))
    product_uom = fields.Many2one(
        comodel_name="product.uom", string="Product Unit of Measure",
        default=_get_uom, required=True, readonly=True,
        states={"new": [("readonly", False)]})
    lot_id = fields.Many2one(
        comodel_name="stock.production.lot", string="Lot/Serial Number",
        readonly=True, states={"new": [("readonly", False)]},)
    location_id = fields.Many2one(
        comodel_name="stock.location", string="Location",
        default=_get_default_location_id,
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
    stock_scrap_ids = fields.One2many(
        comodel_name='stock.scrap', string='Scraps',
        inverse_name='qc_issue_id')
    stock_scrap_qty = fields.Integer(compute=_compute_stock_scrap_qty)

    _group_by_full = {
        'stage_id': _read_group_stage_ids
    }

    def issue_stage_find(self, cases, team, domain=None, order='sequence'):
        """ Override of the base.stage method
            Parameter of the stage search taken from the problem:
            - team_id: if set, stages must belong to this team or
              be a default stage; if not set, stages must be default
              stages
        """
        team_ids = set()
        if team:
            team_ids.add(team.id)
        for issue in cases:
            if issue.team_id:
                team_ids.add(issue.team_id.id)
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
        stage = self.env['qc.issue.stage'].search(
            search_domain, order=order, limit=1)
        return stage

    @api.multi
    def write(self, vals):
        stage_obj = self.env['qc.issue.stage']
        state = vals.get('state')
        if state:
            if len(self.mapped('qc_team_id')) > 1:
                raise UserError(_(
                    "Every issue must have the same QC team to perform this "
                    "action."))
            team = self[0].qc_team_id
            stage = self.issue_stage_find([], team, [('state', '=', state)])
            if stage:
                vals.update({'stage_id': stage.id})
            return super(QualityControlIssue, self).write(vals)
        team_id = vals.get('qc_team_id')
        if team_id is not None:
            team = self.env['qc.team'].browse(team_id)
            stage = self.issue_stage_find([], team, [('fold', '=', False)])
            if stage:
                vals.update({'stage_id': stage.id})
        stage_id = vals.get('stage_id')
        if stage_id:
            state = stage_obj.browse(stage_id).state
            if state:
                vals.update({'state': state})
        return super(QualityControlIssue, self).write(vals)

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

    @api.multi
    def scrap_products(self):
        self.ensure_one()
        return {
            'name': _('Scrap'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.scrap',
            'view_id': self.env.ref('stock.stock_scrap_form_view2').id,
            'type': 'ir.actions.act_window',
            'context': {
                'default_qc_issue_id': self.id,
                'default_location_id': self.location_id.id,
                'default_product_id': self.product_id.id,
                'default_scrap_qty': self.product_qty,
                'default_product_uom_id': self.product_uom.id,
                'default_lot_id': self.lot_id.id,
            },
            'target': 'new',
        }

    @api.multi
    def action_view_stock_scrap(self):
        action = self.env.ref('stock.action_stock_scrap')
        result = action.read()[0]
        lines = self.stock_scrap_ids
        # choose the view_mode accordingly
        if len(lines) != 1:
            result['domain'] = "[('id', 'in', " + \
                               str(lines.ids) + ")]"
        elif len(lines) == 1:
            res = self.env.ref('stock.stock_scrap_form_view', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = lines.id
        return result
