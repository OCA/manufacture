# Copyright (C) 2019 Akretion (http://www.akretion.com). All Rights Reserved
# @author David BEAL <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
import logging

from odoo import _, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DT_FORMAT


logger = logging.getLogger(__name__)
INFO = "Previous write can lead to concurrency updates. " \
       "Ensure this event is not occurs frequently in your process"


class MrpUnbuild(models.Model):
    _inherit = "mrp.unbuild"

    def action_unbuild(self):
        # We collect all components grouped by unbuild order
        components_by_serial = {
            unbuild: unbuild.bom_id.bom_line_ids.mapped(
                "product_id").filtered(lambda s: s.tracking == "serial")
            for unbuild in self}
        components_by_lot = {
            unbuild: unbuild.bom_id.bom_line_ids.mapped(
                "product_id").filtered(lambda s: s.tracking == "lot")
            for unbuild in self}
        for unbuild in self:
            components = components_by_serial[unbuild] | components_by_lot[
                unbuild]
            # To bypass Odoo limitation in use cases we need
            # to make components as untracked
            components.write({"tracking": "none"})
            logger.info(INFO)
        res = super().action_unbuild()
        if not components_by_serial and not components_by_lot:
            return res
        for unbuild in self:
            # we revert to previous state
            components_by_serial[unbuild].write({"tracking": "serial"})
            components_by_lot[unbuild].write({"tracking": "lot"})
            components = [x.name for x in components_by_lot[unbuild]]
            components.extend([x.name for x in components_by_serial[unbuild]])
            unbuild.message_post(
                body=_("Components %s have been temporarily untracked "
                       "to allow sucessful unbuild") % components)
            unbuild._create_lots()
        return res

    def _create_lots(self):
        for rec in self.produce_line_ids.filtered(
                lambda s: s.product_id.tracking != 'none'):
            lot = self.env['stock.production.lot'].create(
                self._prepare_lots_for_unbuild(rec.product_id))
            rec._get_move_lines()[0].write({"lot_id": lot.id})

    def _prepare_lots_for_unbuild(self, product):
        return {
            "name": datetime.now().strftime(DT_FORMAT),
            "product_id": product.id}
