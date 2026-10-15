# Copyright 2023 Quartile
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    owner_id = fields.Many2one(
        "res.partner",
        "Assign Owner",
        readonly=True,
        check_company=True,
        help="Produced products will be assigned to this owner.",
    )
    owner_restriction = fields.Selection(related="picking_type_id.owner_restriction")

    @api.model_create_multi
    def create(self, vals_list):
        """Apply the owner carried over from a merge operation, if any.

        ``action_merge`` puts the owner shared by the merged MOs in the context
        (see ``action_merge``) because the merged MO is built by ``create``, and
        the owner has to be on it before ``action_confirm`` reserves the
        components. The key is dropped for the nested records created along the
        way -- only the MO itself is concerned.
        """
        merged_owner_id = self.env.context.get("mrp_merged_owner_id")
        if merged_owner_id:
            vals_list = [dict(vals, owner_id=merged_owner_id) for vals in vals_list]
        return super(
            MrpProduction, self.with_context(mrp_merged_owner_id=False)
        ).create(vals_list)

    def write(self, vals):
        if "owner_id" in vals:
            # Reservations made under the previous owner no longer apply: release
            # them so that the components get reserved again for the new one.
            productions = self.filtered(
                lambda p: p.owner_restriction in ("unassigned_owner", "picking_partner")
            )
            productions.move_raw_ids.filtered(
                lambda m: m.state not in ("done", "cancel")
            )._do_unreserve()
        return super().write(vals)

    def action_merge(self):
        """Carry the owner over to the merged MO when all sources agree on it.

        Sources with different owners, or a mix of owned and unowned ones, leave
        the merged MO unowned: no single owner applies to the whole quantity.
        """
        owners = self.owner_id
        if len(owners) == 1 and len(self.filtered("owner_id")) == len(self):
            self = self.with_context(mrp_merged_owner_id=owners.id)
        return super().action_merge()
