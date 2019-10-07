# (c) 2014 Daniel Campos <danielcampos@avanzosc.es>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models, _


class ProjectProject(models.Model):
    _inherit = 'project.project'

    def _compute_mrp_production_count(self):
        production = self.env['mrp.production']
        for project in self:
            domain = [('project_id', '=', self.id)]
            project.production_count = production.search_count(domain)

    @api.multi
    def mrp_production_tree_view(self):
        self.ensure_one()
        domain = [('project_id', '=', self.ids)]
        return {
            'name': _('Manufacturing Orders'),
            'domain': domain,
            'res_model': 'mrp.production',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                Manufacturing Orders can be related to your project.</p><p>
                Go to your Manufacturing Order and to click in the respective
                button to relate Manufacturing Orders with your Project.
                </p>'''),
            'limit': 80,
            'context': '''
                {{'search_default_project_id': [{0}],
                'default_project_id': {0}}}
                '''.format(self.id)
        }

    production_count = fields.Integer(
        string='Manufacturing Count',
        compute=_compute_mrp_production_count
    )
    automatic_creation = fields.Boolean(_('Automatic Creation'))
