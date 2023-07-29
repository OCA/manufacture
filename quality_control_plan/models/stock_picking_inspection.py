# Copyright 2019 Marcelo Frare (Ass. PNLUG - Gruppo Odoo <http://odoo.pnlug.it>)
# Copyright 2019 Stefano Consolaro (Ass. PNLUG - Gruppo Odoo <http://odoo.pnlug.it>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockPicking(models.Model):
    """
    Extend picking method
    """

    _inherit = "stock.picking"

    def action_done(self):
        """
        Extend actions on done stock move adding inspection defined on Partner
        """

        # does original action and memorize result
        result = super(StockPicking, self).action_done()

        # gets model of the inspection
        inspection_model = self.env["qc.inspection"]

        # for each line moved
        for operation in self.move_lines:
            # gets quality trigger associate to movement type
            qc_trigger = self.env["qc.trigger"].search(
                [("picking_type_id", "=", self.picking_type_id.id)]
            )

            # gets partner associate to movement
            partner = self.partner_id

            # gets trigger for movement type on partner
            trigger_line = self.env["qc.trigger.partner_line"].search(
                [("partner", "=", partner.id), ("trigger", "=", qc_trigger.id)], limit=1
            )

            # adds new ispection
            if trigger_line:
                inspection_model._make_inspection(operation, trigger_line)

        return result
