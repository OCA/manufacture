# -*- coding: utf-8 -*-
# © 2015 Daniel Campos
# © 2015 Pedro M. Baeza
# © 2015 Ana Juaristi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.multi
    def _prepare_wc_line(self, wc_use, level=0, factor=1):
        res = super(MrpBom, self)._prepare_wc_line(
            wc_use, level=level, factor=factor)
        res['init_without_material'] = wc_use.init_without_material
        return res
