# Copyright 2010 NaN Projectes de Programari Lliure, S.L.
# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2014 Oihane Crucelaegui - AvanzOSC
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Simone Rubino - Agile Business Group
# Copyright 2019 Marcelo Frare (Ass. PNLUG - Gruppo Odoo <http://odoo.pnlug.it>)
# Copyright 2019 Stefano Consolaro (Ass. PNLUG - Gruppo Odoo <http://odoo.pnlug.it>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class QcTriggerPartnerLine(models.Model):
    """
    Extends quality trigger with partner control plan
    """

    _inherit = "qc.trigger.line"

    # model
    _name = "qc.trigger.partner_line"

    # new fields
    # reference partner
    partner = fields.Many2one(comodel_name="res.partner")
    # control plan to use
    plan_id = fields.Many2one("qc.plan", "Plan", required=True)


class QcTriggerProductLine(models.Model):
    """
    Extends product model with a field to store quality control plan assigned
    """

    _inherit = ["qc.trigger.product_template_line"]

    # new filed
    # product's control plan
    plan_id = fields.Many2one("qc.plan", "Plan")


class QcTriggerCategoryLine(models.Model):
    """
    Extends product category model with a field to store quality control plan assigned
    """

    _inherit = ["qc.trigger.product_category_line"]

    # new filed
    # sets product category's control plan
    plan_id = fields.Many2one("qc.plan", "Plan")
