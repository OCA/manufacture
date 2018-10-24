# (c) 2018 Jose Luis Sandoval Alaguna <jose.alaguna@rotafilo.com.tr>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    task_ids = fields.One2many(
        comodel_name="project.task",
        inverse_name="workorder",
        string="Tasks"
    )
