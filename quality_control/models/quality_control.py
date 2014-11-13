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

from openerp.tools.translate import _
from openerp.osv import orm, fields
import time


class QcProofMethod(orm.Model):
    """
    This model stores a method for doing a test. Examples of methods are:
    "Eu.Pharm.v.v. (2.2.32)" or "HPLC"
    """
    _name = 'qc.proof.method'
    _description = 'Method'

    _columns = {
        'name': fields.char('Name', size=100, required=True, select="1",
                            translate=True),
        'active': fields.boolean('Active'),
    }

    _defaults = {
        'active': True,
    }


class QcPosibleValue(orm.Model):
    """
    This model stores all possible values of qualitative proof.
    """
    _name = 'qc.posible.value'

    _columns = {
        'name': fields.char('Name', size=200, required=True, select="1",
                            translate=True),
        'active': fields.boolean('Active'),
        'ok': fields.boolean('Correct answer',
                             help="When this field is marked, the answer "
                                  "is considered correct."),
    }

    _defaults = {
        'active': True,
    }

    def search(self, cr, uid, args, offset=0, limit=None, order=None,
               context=None, count=False):
        if context is None:
            context = {}
        if context.get('proof_id'):
            ctx = context.copy()
            del ctx['proof_id']
            proof = self.pool['qc.proof'].browse(cr, uid, context['proof_id'],
                                                 ctx)
            result = [x.id for x in proof.value_ids]
            args = args[:]
            args.append(('id', 'in', result))
        return super(QcPosibleValue, self).search(cr, uid, args, offset, limit,
                                                  order, context, count)


class QcProof(orm.Model):
    """
    This model stores proofs which will be part of a test. Proofs are
    classified between qualitative (such as color) and quantitative (such as
    density).

    Proof must be related with method, and Poof-Method relation must be unique

    A name_search on thish model will search on 'name' field but also on any of
    its synonyms.
    """
    _name = 'qc.proof'

    def _synonyms(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for proof in self.browse(cr, uid, ids, context=context):
            texts = []
            for syn in proof.synonym_ids:
                texts.append(syn.name)
            result[proof.id] = ', '.join(texts)
        return result

    _columns = {
        'name': fields.char('Name', size=200, required=True, select="1",
                            translate=True),
        'ref': fields.char('Code', size=30, select="1"),
        'active': fields.boolean('Active'),
        'synonym_ids': fields.one2many('qc.proof.synonym', 'proof_id',
                                       'Synonyms'),
        'type': fields.selection([('qualitative', 'Qualitative'),
                                  ('quantitative', 'Quantitative')], 'Type',
                                 select="1", required=True),
        'value_ids': fields.many2many('qc.posible.value',
                                      'qc_proof_posible_value_rel', 'proof_id',
                                      'posible_value_id', 'Posible Values'),
        'synonyms': fields.function(_synonyms, method=True, type='char',
                                    string='Synonyms', store=False),
    }

    _defaults = {
        'active': True,
    }

    def name_search(self, cr, uid, name='', args=None, operator='ilike',
                    context=None, limit=None):
        result = super(QcProof, self).name_search(cr, uid, name=name,
                                                  args=args, operator=operator,
                                                  context=context, limit=limit)
        synonym_obj = self.pool['qc.proof.synonym']
        if name:
            ids = [x[0] for x in result]
            new_ids = []
            syns = synonym_obj.name_search(cr, uid, name=name, args=args,
                                           operator=operator, context=context,
                                           limit=limit)
            syns = [x[0] for x in syns]
            for syn in synonym_obj.browse(cr, uid, syns, context=context):
                if syn.proof_id.id not in ids:
                    new_ids.append(syn.proof_id.id)
            result += self.name_get(cr, uid, new_ids, context=context)
        return result

#     def name_get(self, cr, uid, ids, context=None):
#         result = []
#         for proof in self.browse(cr, uid, ids, context=context):
#             text = proof.name
#             if proof.synonym_ids:
#                 text += "  [%s]" % proof.synonyms
#             result.append((proof.id, text))
#         return result


class QcProofSynonym(orm.Model):
    """
    Proofs may have synonyms. These are used because suppliers may use
    different names for the same proof.
    """
    _name = 'qc.proof.synonym'

    _columns = {
        'name': fields.char('Name', size=200, required=True, select="1",
                            translate=True),
        'proof_id': fields.many2one('qc.proof', 'Proof', required=True),
    }


class QcTestTemplateCategory(orm.Model):
    """
    This model is used to categorize proof templates.
    """
    _name = 'qc.test.template.category'
    _description = 'Test Template Category'

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        reads = self.read(cr, uid, ids, ['name', 'parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1] + ' / ' + name
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    def _check_recursion(self, cr, uid, ids):
        level = 100
        while len(ids):
            cr.execute('SELECT DISTINCT parent_id FROM'
                       ' qc_test_template_category WHERE id IN (' +
                       ','.join(map(str, ids)) + ')')
            ids = [x[0] for x in cr.fetchall() if x[0] is not None]
            if not level:
                return False
            level -= 1
        return True

    _columns = {
        'name': fields.char('Category Name', required=True, size=64,
                            translate=True),
        'parent_id': fields.many2one('qc.test.template.category',
                                     'Parent Category', select=True),
        'complete_name': fields.function(_name_get_fnc, method=True,
                                         type="char", string='Full Name'),
        'child_ids': fields.one2many('qc.test.template.category', 'parent_id',
                                     'Child Categories'),
        'active': fields.boolean('Active',
                                 help="The active field allows you to hide the"
                                 " category without removing it."),
    }

    _constraints = [
        (_check_recursion,
         _('Error ! You can not create recursive categories.'), ['parent_id'])
    ]

    _defaults = {
        'active': 1,
    }


class QcTestTemplateTrigger(orm.Model):
    _name = 'qc.test.template.trigger'
    _description = 'Test Template Trigger'

    _columns = {
        'name': fields.char('Name', size=64, required=True, readonly=False,
                            translate=True),
        'active': fields.boolean('Active', required=False),
    }

    _defaults = {
        'active': 1,
    }


class QcTestTemplate(orm.Model):
    """
    A template is a group of proofs to with the values that make them valid.
    """
    _name = 'qc.test.template'
    _description = 'Test Template'

    def _links_get(self, cr, uid, context=None):
        # TODO: Select models
        link_obj = self.pool['res.request.link']
        ids = link_obj.search(cr, uid, [], context=context)
        res = link_obj.read(cr, uid, ids, ['object', 'name'], context=context)
        return [(r['object'], r['name']) for r in res]

    def _default_name(self, cr, uid, context=None):
        if context and context.get('reference_model', False):
            templ_id = context.get('reference_id')
            if not templ_id:
                templ_id = context.get('active_id')
            if templ_id:
                source = self.pool[context['reference_model']].browse(
                    cr, uid, id, context=context)
                if hasattr(source, 'name'):
                    return source.name

    def _default_object_id(self, cr, uid, context=None):
        if context and context.get('reference_model', False):
            return '%s,%d' % (context['reference_model'],
                              context['reference_id'])
        else:
            return False

    def _default_type(self, cr, uid, context=None):
        if context and context.get('reference_model'):
            return 'related'
        else:
            return False

    _columns = {
        'active': fields.boolean('Active', select="1"),
        'name': fields.char('Name', size=200, required=True, translate=True,
                            select="1"),
        'test_template_line_ids': fields.one2many('qc.test.template.line',
                                                  'test_template_id', 'Lines'),
        'object_id': fields.reference('Reference Object', selection=_links_get,
                                      size=128),
        'fill_correct_values': fields.boolean('Fill With Correct Values'),
        'type': fields.selection([('generic', 'Generic'),
                                  ('related', 'Related')], 'Type', select="1"),
        'category_id': fields.many2one('qc.test.template.category',
                                       'Category'),
        'trig_on': fields.many2one('qc.test.template.trigger', 'Trigger'),
    }

    _defaults = {
        'name': _default_name,
        'active': True,
        'object_id': _default_object_id,
        'type': _default_type,
    }


class QcTestTemplateLine(orm.Model):
    """
    Each test template line has a reference to a proof and the valid
    value/values.
    """
    _name = 'qc.test.template.line'
    _description = 'Test Template Line'
    _order = 'sequence asc'
    _rec_name = 'sequence'

    def onchange_proof_id(self, cr, uid, ids, proof_id, context=None):
        if not proof_id:
            return {}
        proof = self.pool['qc.proof'].browse(cr, uid, proof_id,
                                             context=context)
        return {'value': {'type': proof.type}}

    _columns = {
        'sequence': fields.integer('Sequence', required=True),
        'test_template_id': fields.many2one('qc.test.template',
                                            'Test Template', select="1"),
        'proof_id': fields.many2one('qc.proof', 'Question', required=True,
                                    select="1"),
        'valid_value_ids': fields.many2many('qc.posible.value',
                                            'qc_template_value_rel',
                                            'template_line_id', 'value_id',
                                            'Answers'),
        'method_id': fields.many2one('qc.proof.method', 'Method', select="1"),
        'notes': fields.text('Notes'),
        'min_value': fields.float('Min', digits=(16, 5)),  # Quantitative only
        'max_value': fields.float('Max', digits=(15, 5)),  # Quantitative only
        'uom_id': fields.many2one('product.uom', 'Uom'),   # Quantitative only
        'type': fields.selection([('qualitative', 'Qualitative'),
                                  ('quantitative', 'Quantitative')],
                                 'Type', select="1"),
    }

    _defaults = {
        'sequence': 1,
    }


class QcTest(orm.Model):
    """
    This model contains an instance of a test template.
    """
    _name = 'qc.test'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    def _success(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for test in self.browse(cr, uid, ids, context=context):
            success = False
            if len(test.test_line_ids):
                success = True
                proof = {}
                for line in test.test_line_ids:
                    proof[line.proof_id.id] = (proof.get(line.proof_id.id,
                                                         False)
                                               or line.success)
                for p in proof:
                    if not proof[p]:
                        success = False
                        break
            result[test.id] = success
        return result

    def _links_get(self, cr, uid, context=None):
        # TODO: Select models
        link_obj = self.pool['res.request.link']
        ids = link_obj.search(cr, uid, [], context=context)
        res = link_obj.read(cr, uid, ids, ['object', 'name'], context=context)
        return [(r['object'], r['name']) for r in res]

    def _default_object_id(self, cr, uid, context=None):
        if context and context.get('reference_model', False):
            return '%s,%d' % (context['reference_model'],
                              context['reference_id'])
        else:
            return False

    _columns = {
        'name': fields.datetime('Date', required=True, readonly=True,
                                states={'draft': [('readonly', False)]},
                                select="1"),
        'object_id': fields.reference('Reference', selection=_links_get,
                                      size=128, readonly=True,
                                      states={'draft': [('readonly', False)]},
                                      select="1"),
        'test_template_id': fields.many2one('qc.test.template', 'Test',
                                            states={'success':
                                                    [('readonly', True)],
                                                    'failed':
                                                    [('readonly', True)]},
                                            select="1"),
        'test_line_ids': fields.one2many('qc.test.line', 'test_id',
                                         'Test Lines',
                                         states={'success':
                                                 [('readonly', True)],
                                                 'failed':
                                                 [('readonly', True)]}),
        'test_internal_note': fields.text('Internal Note',
                                          states={'success':
                                                  [('readonly', True)],
                                                  'failed':
                                                  [('readonly', True)]}),
        'test_external_note': fields.text('External Note',
                                          states={'success':
                                                  [('readonly', True)],
                                                  'failed':
                                                  [('readonly', True)]}),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('waiting', 'Waiting Supervisor Approval'),
            ('success', 'Quality Success'),
            ('failed', 'Quality Failed'),
            ('canceled', 'Canceled'),
        ], 'State', readonly=True, select="1"),
        'success': fields.function(_success, method=True, type='boolean',
                                   string='Success',
                                   help='This field will be active if all'
                                   ' tests have succeeded.', select="1",
                                   store=True),
        'enabled': fields.boolean('Enabled', readonly=True,
                                  help='If a quality control test is not'
                                  ' enabled it means it can not be moved from'
                                  ' "Quality Success" or "Quality Failed"'
                                  ' state.', select="1"),
    }
    _defaults = {
        'name': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'state': 'draft',
        'object_id': _default_object_id,
        'enabled': True,
    }

    def copy(self, cr, uid, copy_id, default=None, context=None):
        if default is None:
            default = {}
        default['name'] = time.strftime('%Y-%m-%d %H:%M:%S')
        return super(QcTest, self).copy(
            cr, uid, copy_id, default, context=context)

    def create(self, cr, uid, datas, context=None):
        if context and context.get('reference_model', False):
            datas['object_id'] = (context['reference_model'] + "," +
                                  str(context['reference_id']))
        return super(orm.Model, self).create(cr, uid, datas, context=context)

    def qc_test_success(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {
            'state': 'success'
        }, context=context)
        return True

    def qc_test_failed(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {
            'state': 'failed'
        }, context=context)
        return True

    def test_state(self, cr, uid, ids, mode, *args):
        quality_check = False
        if mode == 'failed':
            return not quality_check
        if mode == 'success':
            return quality_check
        return False

    def set_test_template(self, cr, uid, ids, template_id, force_fill=False,
                          context=None):
        if context is None:
            context = {}
        test_obj = self.pool['qc.test']
        test_line_obj = self.pool['qc.test.line']
        for test_id in ids:
            test_obj.write(cr, uid, test_id, {
                'test_template_id': template_id
            }, context)
            test = test_obj.browse(cr, uid, test_id, context=context)

            if len(test.test_line_ids) > 0:
                test_line_obj.unlink(cr, uid,
                                     [x.id for x in test.test_line_ids],
                                     context=context)
            test_lines = self._prepare_test_lines(
                cr, uid, test, force_fill=force_fill, context=context)
            test_obj.write(cr, uid, test_id, {'test_line_ids': test_lines},
                           context=context)

    def _prepare_test_lines(self, cr, uid, test, force_fill=False,
                            context=None):
        new_data = []
        fill = test.test_template_id.fill_correct_values
        for line in test.test_template_id.test_template_line_ids:
            data = self._prepare_test_line(
                cr, uid, test, line, fill=fill or force_fill, context=context)
            new_data.append((0, 0, data))
        return new_data

    def _prepare_test_line(self, cr, uid, test, line, fill=None, context=None):
        data = {}
        data = {'test_id': test.id,
                'method_id': line.method_id.id,
                'proof_id': line.proof_id.id,
                'test_template_line_id': line.id,
                'notes': line.notes,
                'min_value': line.min_value,
                'max_value': line.max_value,
                'uom_id': line.uom_id.id,
                'test_uom_id': line.uom_id.id,
                'proof_type': line.type,
                }
        if fill:
            if line.type == 'qualitative':
                # Fill with the first correct value found.
                data['actual_value_ql'] = (
                    len(line.valid_value_ids) and
                    line.valid_value_ids[0] and
                    line.valid_value_ids[0].id or False)
            else:
                # Fill with value inside range.
                data['actual_value_qt'] = line.min_value
                data['test_uom_id'] = line.uom_id.id
        data['valid_value_ids'] = [(6, 0, [x.id for x in
                                           line.valid_value_ids])]
        return data


class QcTestLine(orm.Model):
    """
    Each test line has a value and a reference to a proof template line.
    """
    _name = 'qc.test.line'
    _rec_name = 'proof_id'

    def quality_test_check(self, cr, uid, ids, field_name, field_value,
                           context=None):
        res = {}
        lines = self.browse(cr, uid, ids, context=None)
        for line in lines:
            if line.proof_type == 'qualitative':
                res[line.id] = self.quality_test_qualitative_check(
                    cr, uid, line, context=None)
            else:
                res[line.id] = self.quality_test_quantitative_check(
                    cr, uid, line, context=None)
        return res

    def quality_test_qualitative_check(self, cr, uid, test_line, context=None):
        if test_line.actual_value_ql in test_line.valid_value_ids:
            return test_line.actual_value_ql.ok
        else:
            return False

    def quality_test_quantitative_check(self, cr, uid, test_line,
                                        context=None):
        amount = self.pool['product.uom']._compute_qty(
            cr, uid, test_line.uom_id.id, test_line.actual_value_qt,
            test_line.test_uom_id.id)
        if amount >= test_line.min_value and amount <= test_line.max_value:
            return True
        else:
            return False

    _columns = {
        'test_id': fields.many2one('qc.test', 'Test'),
        'test_template_line_id': fields.many2one('qc.test.template.line',
                                                 'Test Template Line',
                                                 readonly=True),
        'proof_id': fields.many2one('qc.proof', 'Question', readonly=True),
        'method_id': fields.many2one('qc.proof.method', 'Method',
                                     readonly=True),
        'valid_value_ids': fields.many2many('qc.posible.value',
                                            'qc_test_value_rel',
                                            'test_line_id', 'value_id',
                                            'Answers'),
        'actual_value_qt': fields.float('Qt.Value', digits=(16, 5),
                                        help="Value of the result if it is a"
                                        " quantitative proof."),
        'actual_value_ql': fields.many2one('qc.posible.value', 'Ql.Value',
                                           help="Value of the result if it is"
                                           " a qualitative proof."),
        'notes': fields.text('Notes', readonly=True),
        'min_value': fields.float('Min', digits=(16, 5), readonly=True,
                                  help="Minimum valid value if it is a"
                                  " quantitative proof."),
        'max_value': fields.float('Max', digits=(16, 5), readonly=True,
                                  help="Maximum valid value if it is a"
                                  " quantitative proof."),
        'uom_id': fields.many2one('product.uom', 'Uom', readonly=True,
                                  help="UoM for minimum and maximum values if"
                                  " it is a quantitative proof."),
        'test_uom_id': fields.many2one('product.uom', 'Uom Test',
                                       help="UoM of the value of the result"
                                       " if it is a quantitative proof."),
        'proof_type': fields.selection([('qualitative', 'Qualitative'),
                                        ('quantitative', 'Quantitative')],
                                       'Proof Type', readonly=True),
        'success': fields.function(quality_test_check, type='boolean',
                                   method=True, string="Success?", select="1"),
    }

    def onchange_actual_value_qt(self, cr, uid, ids, uom_id, test_uom_id,
                                 actual_value_qt, min_value, max_value,
                                 context=None):
        res = {}
        if actual_value_qt:
            amount = self.pool['product.uom']._compute_qty(cr, uid, uom_id,
                                                           actual_value_qt,
                                                           test_uom_id)
            if amount >= min_value and amount <= max_value:
                res['success'] = True
            else:
                res['success'] = False
        return {'value': res}

    def onchange_actual_value_ql(self, cr, uid, ids, actual_value_ql,
                                 valid_value_ids, context=None):
        res = {}
        value_obj = self.pool['qc.posible.value']
        if actual_value_ql:
            valid = valid_value_ids[0][2]
            if actual_value_ql in valid:
                value = value_obj.browse(cr, uid, actual_value_ql, context)
                res['success'] = value.ok
            else:
                res['success'] = False
        return {'value': res}
