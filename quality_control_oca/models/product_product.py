# -*- coding: utf-8 -*-
# Copyright 2010 NaN Projectes de Programari Lliure, S.L.
# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2014 Oihane Crucelaegui - AvanzOSC
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    qc_triggers = fields.One2many(
        comodel_name="qc.trigger.product_line", inverse_name="product",
        string="Quality control triggers")
