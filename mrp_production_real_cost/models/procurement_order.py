# -*- coding: utf-8 -*-
# © 2016 Eska Yazılım ve Danışmanlık A.Ş. - Levent Karakaş
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, api


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.model
    def _check(self, procurement):
        if procurement.production_id:
            # This is needed because commit
            # https://github.com/odoo/odoo/commit/
            # 6f29bfc181d23d70d29776d96b4318e9ee2c93a9
            # introduces a weird behavior on the next call, provoking an error.
            procurement.production_id.sudo().refresh()
        return super(ProcurementOrder, self)._check(procurement)
