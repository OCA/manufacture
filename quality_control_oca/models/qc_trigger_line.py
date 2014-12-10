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

    def get_test_for_product(self, trigger, product):
        """Overridable method for getting test associated to a product.
        Each inherited model will complete this module to make the search by
        product, template or category.
        :param trigger: Trigger instance.
        :param product: Product instance.
        :return: Set of tests that matches to the given product and trigger.
        """
        return set()


class QcTriggerProductCategoryLine(models.Model):
    _inherit = "qc.trigger.line"
    _name = "qc.trigger.product_category_line"

    product_category = fields.Many2one(comodel_name="product.category")

    def get_test_for_product(self, trigger, product):
        tests = super(QcTriggerProductCategoryLine,
                      self).get_test_for_product(trigger, product)
        category = product.categ_id
        while category:
            for trigger_line in category.qc_triggers:
                if trigger_line.trigger.id == trigger.id:
                    tests.add(trigger_line.test)
            category = category.parent_id
        return tests


class QcTriggerProductTemplateLine(models.Model):
    _inherit = "qc.trigger.line"
    _name = "qc.trigger.product_template_line"

    product_template = fields.Many2one(comodel_name="product.template")

    def get_test_for_product(self, trigger, product):
        tests = super(QcTriggerProductTemplateLine,
                      self).get_test_for_product(trigger, product)
        for trigger_line in product.product_tmpl_id.qc_triggers:
            if trigger_line.trigger.id == trigger.id:
                tests.add(trigger_line.test)
        return tests


class QcTriggerProductLine(models.Model):
    _inherit = "qc.trigger.line"
    _name = "qc.trigger.product_line"

    product = fields.Many2one(comodel_name="product.product")

    def get_test_for_product(self, trigger, product):
        tests = super(QcTriggerProductLine, self).get_test_for_product(
            trigger, product)
        for trigger_line in product.qc_triggers:
            if trigger_line.trigger.id == trigger.id:
                tests.add(trigger_line.test)
        return tests
