# Copyright 2019-20 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MrpWorkOrder(models.Model):
    _inherit = "mrp.workorder"
    _order = "production_id, sequence, id"

    sequence = fields.Integer()

    def _assign_sequence_on_create(self, values_list):
        """Assign sequence number for manually added operations"""
        new_wos_production_ids_without_seq = {
            vals["production_id"] for vals in values_list if not vals.get("sequence")
        }
        if new_wos_production_ids_without_seq:
            max_seq_by_production = self.read_group(
                [("production_id", "in", list(new_wos_production_ids_without_seq))],
                ["sequence:max", "production_id"],
                ["production_id"],
            )
            max_seq_by_prod_id = {
                res["production_id"][0]: res["sequence"]
                for res in max_seq_by_production
            }
            for values in values_list:
                prod_id = values["production_id"]
                values_seq = values.get("sequence")
                max_seq = max_seq_by_prod_id.setdefault(prod_id, 0)
                if values_seq and values_seq > max_seq:
                    max_seq_by_prod_id[prod_id] = values_seq
                    continue
                max_seq_by_prod_id[prod_id] += 1
                values["sequence"] = max_seq_by_prod_id[prod_id]

    @api.model_create_multi
    def create(self, values_list):
        if not self.env.context.get("_bypass_sequence_assignation_on_create"):
            self._assign_sequence_on_create(values_list)
        return super().create(values_list)
