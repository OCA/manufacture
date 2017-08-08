# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import api, _, models, fields


class MrpRepair(models.Model):
    _inherit = "mrp.repair"
    current_revision_id = fields.Many2one(
        'mrp.repair',
        'Current revision',
        readonly=True,
        copy=True)
    old_revision_ids = fields.One2many(
        'mrp.repair',
        'current_revision_id',
        'Old revisions',
        readonly=True,
        context={'active_test': False})
    revision_number = fields.Integer(
        'Revision',
        copy=False)
    unrevisioned_name = fields.Char(
        'Repair Reference',
        copy=True,
        readonly=True)
    active = fields.Boolean(
        'Active',
        default=True,
        copy=True)

    _sql_constraints = [
        ('revision_unique',
         'unique(unrevisioned_name, revision_number, company_id)',
         'Repair Reference and revision must be unique per Company.'),
    ]

    @api.multi
    def copy_mrp_repair(self):
        self.ensure_one()
        old_revision = self.with_context(
            new_mrp_repair_revision=True).copy()
        view_ref = self.env['ir.model.data'].get_object_reference(
            'mrp_repair', 'view_repair_order_form')
        view_id = view_ref and view_ref[1] or False,
        action = {
            'type': 'ir.actions.act_window',
            'name': _('Repair Order'),
            'res_model': 'mrp.repair',
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current',
            'nodestroy': True,
            'context': {'new_mrp_repair_revision': True},
        }
        self.delete_workflow()
        self.create_workflow()
        self.write({'state': 'draft'})
        self.operations.write({'state': 'draft'})
        msg = _('New revision created: %s') % self.name
        self.message_post(body=msg)
        old_revision.operations.write({'state': 'cancel'})
        old_revision.message_post(body=msg)
        return action

    @api.returns('self', lambda value: value.id)
    @api.multi
    def copy(self, defaults=None):
        if not defaults:
            defaults = {}
        if self.env.context.get('new_mrp_repair_revision'):
            mrp_repair_name = self.name
            revno = self.revision_number
            self.write({'revision_number': revno + 1,
                        'name': '%s-%02d' % (self.unrevisioned_name,
                                             revno + 1)
                        })
            defaults.update({'name': mrp_repair_name,
                             'revision_number': revno,
                             'active': False,
                             'state': 'cancel',
                             'current_revision_id': self.id,
                             'unrevisioned_name': self.unrevisioned_name,
                             })
        return super(MrpRepair, self).copy(defaults)

    @api.model
    def create(self, values):
        if 'unrevisioned_name' not in values:
            if values.get('name', '/') == '/':
                seq = self.env['ir.sequence']
                values['name'] = seq.next_by_code('mrp.repair') or '/'
            values['unrevisioned_name'] = values['name']
        return super(MrpRepair, self).create(values)
