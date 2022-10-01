# 2016 Akretion (http://www.akretion.com)
# David BEAL <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MrpWorkcenter(models.Model):
    _inherit = "mrp.workcenter"
    _parent_name = "parent_id"
    _parent_store = True

    parent_id = fields.Many2one(
        comodel_name="mrp.workcenter", string="Parent", index=True
    )
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many(
        comodel_name="mrp.workcenter", inverse_name="parent_id", string="Children"
    )
    parent_level_1_id = fields.Many2one(
        comodel_name="mrp.workcenter",
        compute="_compute_parent_level",
        string="Parent Level 1",
        store=True,
    )
    parent_level_2_id = fields.Many2one(
        comodel_name="mrp.workcenter",
        compute="_compute_parent_level",
        string="Parent Level 2",
        store=True,
    )
    parent_level_3_id = fields.Many2one(
        comodel_name="mrp.workcenter",
        compute="_compute_parent_level",
        string="Parent Level 3",
        store=True,
    )

    def _get_parent_ids(self):
        self.ensure_one()
        if self.parent_id:
            ids = self.parent_id._get_parent_ids()
            ids.append(self.parent_id.id)
        else:
            ids = []
        return ids

    @api.depends("parent_id.parent_id.parent_id.parent_id", "child_ids")
    def _compute_parent_level(self):
        def get_next_level(parent_ids, workcenter):
            return (
                parent_ids
                and parent_ids.pop(0)
                or (workcenter.child_ids and workcenter.id or workcenter.parent_id.id)
            )

        for workcenter in self:
            parent_ids = workcenter._get_parent_ids()
            exclude_ids = [workcenter.id, workcenter.parent_id.id]
            l_id = [False, False, False]

            l_id[0] = get_next_level(parent_ids, workcenter)
            workcenter.parent_level_1_id = (
                l_id[0] if l_id[0] not in exclude_ids else False
            )
            exclude_ids.append(l_id[0])

            l_id[1] = get_next_level(parent_ids, workcenter)
            workcenter.parent_level_2_id = (
                l_id[1] if l_id[1] not in exclude_ids else False
            )
            exclude_ids.append(l_id[1])

            l_id[2] = get_next_level(parent_ids, workcenter)
            workcenter.parent_level_3_id = (
                l_id[2] if l_id[2] not in exclude_ids else False
            )
