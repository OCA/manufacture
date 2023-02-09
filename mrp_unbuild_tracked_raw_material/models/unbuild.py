# Copyright (C) 2019 Akretion (http://www.akretion.com). All Rights Reserved
# @author David BEAL <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from datetime import datetime

from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DT_FORMAT

logger = logging.getLogger(__name__)

MESSAGE = (
    "Some of your components are tracked, you have to specify "
    "a manufacturing order in order to retrieve the correct components."
)
ALTER_MESSAGE = (
    "Alternatively, you may unbuild '%s' tracked product "
    "if you set it as '%s'.\n"
    "In this case lots'll be automatically created for you."
)


class MrpUnbuild(models.Model):
    _inherit = "mrp.unbuild"

    def action_unbuild(self):
        """ We need to catch raise behavior when tracked products
            are unbuild without an original manufacturing order and
            go on with another workflow with
            _bypass_tracked_product_without_mo()
        """
        try:
            res = super().action_unbuild()
        except UserError as err:
            # Unbuild is impossible because of MESSAGE
            # original condition of this raise is :
            # any(produce_move.has_tracking != 'none'
            # and not self.mo_id for produce_move in produce_moves)
            if hasattr(err, "name") and err.name == _(MESSAGE):
                if self.product_id.allow_unbuild_purchased:
                    # In this case it becomes possible to unbuild
                    return self._bypass_tracked_product_without_mo()
                # Here other option to resolve unbuild conditions
                new_message = _(ALTER_MESSAGE) % (
                    self.product_id.name,
                    _("Unbuild Purchased"),
                )
                # We teach user the 2 conditions that make unbuild possible
                raise UserError(_("%s \n\n%s") % (err.name, new_message))
            # Here is the Odoo native raise
            raise err
        return res

    def _bypass_tracked_product_without_mo(self):
        # These moves are already generated with call to
        # super().action_unbuild(). We catch them
        consume_move = self.env["stock.move"].search(
            [("consume_unbuild_id", "=", self.id)]
        )
        produce_moves = self.env["stock.move"].search([("unbuild_id", "=", self.id)])

        # Comes from
        # https://github.com/OCA/ocb/blob/12.0/addons/mrp/models/...
        # mrp_unbuild.py#L117
        if consume_move:
            if consume_move.has_tracking != "none":
                self.env["stock.move.line"].create(
                    {
                        "move_id": consume_move.id,
                        "lot_id": self.lot_id.id,
                        "qty_done": consume_move.product_uom_qty,
                        "product_id": consume_move.product_id.id,
                        "product_uom_id": consume_move.product_uom.id,
                        "location_id": consume_move.location_id.id,
                        "location_dest_id": consume_move.location_dest_id.id,
                    }
                )
            else:
                consume_move.quantity_done = consume_move.product_uom_qty
            consume_move._action_done()

        # Comment from odoo original module:
        # TODO: Will fail if user do more than one unbuild with lot
        # on the same MO. Need to check what other unbuild has aready took
        for produce_move in produce_moves:
            if produce_move.has_tracking != "none":
                if produce_move.product_id.tracking == "serial":
                    # TODO
                    raise UserError(
                        _(
                            "Unbuild of component of tracked as serial "
                            "is not supported for now: contact maintainers of "
                            "'mrp_unbuild_tracked_raw_material' module "
                            "if you want this feature"
                        )
                    )
                lot = self.env["stock.production.lot"].create(
                    self._prepare_lots_for_purchased_unbuild(produce_move.product_id)
                )
                self.env["stock.move.line"].create(
                    {
                        "move_id": produce_move.id,
                        "lot_id": lot.id,
                        "qty_done": produce_move.product_uom_qty,
                        "product_id": produce_move.product_id.id,
                        "product_uom_id": produce_move.product_uom.id,
                        "location_id": produce_move.location_id.id,
                        "location_dest_id": produce_move.location_dest_id.id,
                    }
                )
            else:
                produce_move.quantity_done = produce_move.product_uom_qty
        # comes from native code
        produce_moves._action_done()
        produced_move_line_ids = produce_moves.mapped("move_line_ids").filtered(
            lambda ml: ml.qty_done > 0
        )
        consume_move.move_line_ids.write(
            {"produce_line_ids": [(6, 0, produced_move_line_ids.ids)]}
        )
        self.message_post(
            body=_("Product has been unbuilt without previous manufacturing order")
        )
        return self.write({"state": "done"})

    def _prepare_lots_for_purchased_unbuild(self, product):
        # Customize your data lot with your own code
        return {
            "name": datetime.now().strftime(DT_FORMAT),
            "product_id": product.id,
            "company_id": self.env.company.id,
        }
