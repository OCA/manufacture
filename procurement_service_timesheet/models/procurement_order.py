# -*- coding: utf-8 -*-
# Copyright 2017 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models, api
from odoo.addons.purchase.models.purchase import \
    ProcurementOrder as PurchaseProcurementOrder


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def _run(self):
        if self._is_procurement_service() and self._is_procurement_task():
            self.make_po()
            # Call super in order to create the task
            return super(PurchaseProcurementOrder, self)._run()
        return super(ProcurementOrder, self)._run()
