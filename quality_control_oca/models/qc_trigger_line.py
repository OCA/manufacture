# Copyright 2010 NaN Projectes de Programari Lliure, S.L.
# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2014 Oihane Crucelaegui - AvanzOSC
# Copyright 2017 ForgeFlow S.L.
# Copyright 2017 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


def _filter_trigger_lines(trigger_lines):
    filtered_trigger_lines = []
    unique_tests = []
    for trigger_line in trigger_lines:
        if trigger_line.test not in unique_tests:
            filtered_trigger_lines.append(trigger_line)
            unique_tests.append(trigger_line.test)
    return filtered_trigger_lines


class QcTriggerLine(models.AbstractModel):
    _name = "qc.trigger.line"
    _inherit = "mail.thread"
    _description = "Abstract line for defining triggers"

    trigger = fields.Many2one(comodel_name="qc.trigger", required=True)
    test = fields.Many2one(comodel_name="qc.test", required=True)
    user = fields.Many2one(
        comodel_name="res.users",
        string="Responsible",
        tracking=True,
        default=lambda self: self.env.user,
    )
    partners = fields.Many2many(
        comodel_name="res.partner",
        string="Partners",
        help="If filled, the test will only be created when the action is done"
        " for one of the specified partners. If empty, the test will always be"
        " created.",
        domain="[('parent_id', '=', False)]",
    )

    def get_trigger_line_for_product(self, trigger, product, partner=False):
        """Overridable method for getting trigger_line associated to a product.
        Each inherited model will complete this module to make the search by
        product, template or category.
        :param trigger: Trigger instance.
        :param product: Product instance.
        :return: Set of trigger_lines that matches to the given product and
        trigger.
        """
        return set()
