# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields


class QcTriggerLine(models.AbstractModel):
    _name = "qc.trigger.line"
    _description = "Abstract line for defining triggers"

    trigger = fields.Many2one(comodel_name="qc.trigger", required=True)
    test = fields.Many2one(comodel_name="qc.test", required=True)
    user = fields.Many2one(
        comodel_name='res.users', string='Responsible',
        track_visibility='always', default=lambda self: self.env.user)

    def get_trigger_line_for_product(self, trigger, product):
        """Overridable method for getting trigger_line associated to a product.
        Each inherited model will complete this module to make the search by
        product, template or category.
        :param trigger: Trigger instance.
        :param product: Product instance.
        :return: Set of trigger_lines that matches to the given product and
        trigger.
        """
        return set()


class QcTriggerProductCategoryLine(models.Model):
    _inherit = "qc.trigger.line"
    _name = "qc.trigger.product_category_line"

    product_category = fields.Many2one(comodel_name="product.category")

    def get_trigger_line_for_product(self, trigger, product):
        trigger_lines = super(QcTriggerProductCategoryLine,
                              self).get_trigger_line_for_product(trigger,
                                                                 product)
        category = product.categ_id
        while category:
            for trigger_line in category.qc_triggers:
                if trigger_line.trigger.id == trigger.id:
                    trigger_lines.add(trigger_line)
            category = category.parent_id
        return trigger_lines


class QcTriggerProductTemplateLine(models.Model):
    _inherit = "qc.trigger.line"
    _name = "qc.trigger.product_template_line"

    product_template = fields.Many2one(comodel_name="product.template")

    def get_trigger_line_for_product(self, trigger, product):
        trigger_lines = super(QcTriggerProductTemplateLine,
                              self).get_trigger_line_for_product(trigger,
                                                                 product)
        for trigger_line in product.product_tmpl_id.qc_triggers:
            if trigger_line.trigger.id == trigger.id:
                trigger_lines.add(trigger_line)
        return trigger_lines


class QcTriggerProductLine(models.Model):
    _inherit = "qc.trigger.line"
    _name = "qc.trigger.product_line"

    product = fields.Many2one(comodel_name="product.product")

    def get_trigger_line_for_product(self, trigger, product):
        trigger_lines = super(QcTriggerProductLine,
                              self).get_trigger_line_for_product(trigger,
                                                                 product)
        for trigger_line in product.qc_triggers:
            if trigger_line.trigger.id == trigger.id:
                trigger_lines.add(trigger_line)
        return trigger_lines
