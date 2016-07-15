# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# David BEAL <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
from openerp.osv import orm
from openerp.exceptions import UserError
from lxml import etree
from openerp.tools.translate import _


class SwitchWorkcenter(models.TransientModel):
    _name = 'switch.workcenter'

    workcenter_id = fields.Many2one(
            'mrp.workcenter',
            'Workcenter',
            required=True)

    @api.multi
    def switch_workcenter(self):
        self.ensure_one()
        MrpProdWorkcLine_m = self.env['mrp.production.workcenter.line']
        active_ids = self.env.context.get('active_ids', [])
        vals = {'workcenter_id': self.workcenter_id.id}
        lines = MrpProdWorkcLine_m.browse(active_ids)
        lines.write(vals)
        return True

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super(SwitchWorkcenter, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)
        if self.env.context.get('active_ids') and view_type == 'form':
            line_obj = self.env['mrp.production.workcenter.line']
            parent_id = False
            for line in line_obj.browse(self.env.context['active_ids']):
                if line.state == 'done':
                    raise UserError(
                        _('You can not change the workcenter of a done '
                          'operation'))
                elif not parent_id:
                    parent_id = line.workcenter_id.parent_level_1_id.id
                elif parent_id != line.workcenter_id.parent_level_1_id.id:
                    raise UserError(
                        _('You can only swith workcenter that share the same '
                          'parent level 1'))
            root = etree.fromstring(res['arch'])
            field = root.find(".//field[@name='workcenter_id']")
            field.set(
                'domain',
                "[('parent_level_1_id', '=', %s)]"
                % parent_id
                )
            orm.setup_modifiers(field, root)
            res['arch'] = etree.tostring(root, pretty_print=True)
        return res
