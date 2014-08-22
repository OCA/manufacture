# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 NaN Projectes de Programari Lliure, S.L.
#                    All Rights Reserved.
#                    http://www.NaN-tic.com
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from openerp.osv import orm, fields


class QcTestWizard(orm.TransientModel):
    """
    This wizard is responsible for setting the proof template for a given test.
    This will not only fill in the 'test_template_id' field, but will also fill
    in all lines of the test with the corresponding lines of the template.
    """
    _name = 'qc.test.set.template.wizard'

    def _default_test_template_id(self, cr, uid, context=None):
        id = context.get('active_id', False)
        test = self.pool['qc.test'].browse(cr, uid, id, context=context)
        ids = self.pool['qc.test.template'].search(cr, uid, [('object_id', '=',
                                                              test.object_id)],
                                                   context=context)
        return ids and ids[0] or False

    _columns = {
        'test_template_id': fields.many2one('qc.test.template', 'Template'),
    }

    _defaults = {
        'test_template_id': _default_test_template_id,
    }

    def action_create_test(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids[0], context=context)
        self.pool['qc.test'].set_test_template(cr, uid, [context['active_id']],
                                               wizard.test_template_id.id,
                                               context=context)
        return {
            'type': 'ir.actions.act_window_close',
        }

    def action_cancel(self, cr, uid, ids, context=None):
        return {
            'type': 'ir.actions.act_window_close',
        }
