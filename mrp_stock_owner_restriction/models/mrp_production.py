# Copyright 2023 Quartile
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


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

        ``action_merge`` injects ``default_owner_id_for_merged_mo`` in the
        context so the merged MO can inherit the owner shared by its sources
        (see ``action_merge``). When the key is present we honour it (an empty
        value means the sources had no common owner, so the field is left
        unset). The ``unassigned_owner`` policy is intentionally not handled
        here: it means the picking type reserves from unowned stock, so the MO
        owner must stay empty.
        """
        if "default_owner_id_for_merged_mo" in self.env.context:
            owner_from_ctx = self.env.context.get("default_owner_id_for_merged_mo")
            new_vals_list = []
            for vals_item in vals_list:
                vals = dict(vals_item)
                if owner_from_ctx:
                    vals["owner_id"] = owner_from_ctx
                else:
                    vals.pop("owner_id", None)
                new_vals_list.append(vals)
            vals_list = new_vals_list

        return super(
            MrpProduction, self.with_context(default_owner_id_for_merged_mo=None)
        ).create(vals_list)

    def write(self, vals):
        if "owner_id" in vals:
            for production in self:
                if production.owner_restriction in (
                    "unassigned_owner",
                    "picking_partner",
                ):
                    production.move_line_raw_ids.unlink()
        return super().write(vals)

    def action_merge(self):
        _logger.info(f"Custom action_merge called for MOs: {self.ids}")

        common_owner_id = None
        if self:
            # Check if all MOs to be merged have an owner_id and if it's the same
            first_mo_owner = self[0].owner_id
            if first_mo_owner:  # If the first MO has an owner
                all_same_owner = all(prod.owner_id == first_mo_owner for prod in self)
                if all_same_owner:
                    common_owner_id = first_mo_owner.id
                else:
                    _logger.info(
                        "MOs to be merged have different owner_ids. "
                        "Merged MO will not inherit an owner from this logic.\n"
                    )
            else:
                # Check if all MOs have no owner
                all_no_owner = all(not prod.owner_id for prod in self)
                if all_no_owner:
                    _logger.info(
                        "All MOs to be merged have no owner_id. "
                        "Merged MO will also have no owner_id from this logic."
                    )
                else:
                    _logger.info(
                        "MOs to be merged have mixed owner_id status\n"
                        " (some have, some don't). "
                        "Merged MO will not inherit an owner from this logic."
                    )

        ctx = self.env.context.copy()
        if common_owner_id:
            ctx["default_owner_id_for_merged_mo"] = common_owner_id
            _logger.info(
                "Context set for merge: "
                "default_owner_id_for_merged_mo = {common_owner_id}"
            )
        else:
            # Ensure the key is not in context if no common owner,
            # or if it was there from a previous operation
            ctx.pop("default_owner_id_for_merged_mo", None)
            _logger.info(
                "No common owner_id found for MOs to be merged,"
                " or first MO had no owner. "
                "Context key 'default_owner_id_for_merged_mo' not set or removed."
            )

        # Call the original action_merge with the potentially modified context.
        # The standard action_merge will internally call the .create() method,
        # which we have also overridden.
        return super(MrpProduction, self.with_context(**ctx)).action_merge()
