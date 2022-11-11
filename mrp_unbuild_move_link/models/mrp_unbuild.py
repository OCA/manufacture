from odoo import models


class MrpUnbuild(models.Model):
    _inherit = "mrp.unbuild"

    def _generate_move_from_existing_move(
        self, move, factor, location_id, location_dest_id
    ):
        result = super(MrpUnbuild, self)._generate_move_from_existing_move(
            move, factor, location_id, location_dest_id
        )
        result.origin_mrp_manufacture_move_id = move.id
        return result
