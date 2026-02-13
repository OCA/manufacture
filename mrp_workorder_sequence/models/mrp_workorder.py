# Copyright 2019-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MrpWorkOrder(models.Model):
    _inherit = "mrp.workorder"
    _order = "production_id, sequence, id"

    def _get_default_sequence(self):
        production_id = self.env.context.get("default_production_id")
        if production_id:
            last_wo = self.search(
                [("production_id", "=", production_id)], order="sequence desc", limit=1
            )
            if last_wo:
                return last_wo.sequence + 1
        return 1

    sequence = fields.Integer(default=_get_default_sequence)

    def _assign_sequence_on_create(self, values_list):
        """Assign sequence number for manually added operations"""
        prod_ids = [v["production_id"] for v in values_list if v.get("production_id")]
        if not prod_ids:
            return

        max_seq_by_production = self.read_group(
            [("production_id", "in", list(set(prod_ids)))],
            ["sequence:max", "production_id"],
            ["production_id"],
        )

        max_map = {
            res["production_id"][0]: (res["sequence"] or 0)
            for res in max_seq_by_production
        }

        for values in values_list:
            p_id = values.get("production_id")
            if not values.get("sequence") or (
                values.get("sequence") == 1 and max_map.get(p_id, 0) >= 1
            ):
                new_seq = max_map.get(p_id, 0) + 1
                values["sequence"] = new_seq
                max_map[p_id] = new_seq
            else:
                if values["sequence"] > max_map.get(p_id, 0):
                    max_map[p_id] = values["sequence"]

    @api.model_create_multi
    def create(self, values_list):
        if not self.env.context.get("_bypass_sequence_assignation_on_create"):
            self._assign_sequence_on_create(values_list)
        return super().create(values_list)
