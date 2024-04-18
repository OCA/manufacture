import logging

from odoo import _, api, exceptions, fields, models
from odoo.tools.safe_eval import safe_eval

logger = logging.getLogger(__name__)


def check_domain(domain, values, current_name, parent_name):

    if domain is None or not isinstance(domain, str):
        return True

    domain = domain.replace("'", '"')
    domain = domain.replace('"="', '"=="')
    domain = safe_eval(domain.replace("!==", "!="))

    if len(domain) == 0:
        return True

    if len(domain) == 1:
        domain.append(True)
    if domain[0] not in ["&", "|"]:
        domain.insert(0, "&")

    # We reverse to evaluate the domain using RPN
    rpn_domain = reversed(domain)

    operand_stack = []

    for token in rpn_domain:
        if token == "&" or token == "|":
            op_b = operand_stack.pop()
            op_a = operand_stack.pop()
            result = evaluate_operator(
                token, op_b, op_a, values, current_name, parent_name
            )
            operand_stack.append(result)
        else:
            operand_stack.append(token)

    return operand_stack.pop()


def evaluate_domain_operand(domain, values, current_name, parent_name):
    if isinstance(domain, bool):
        return domain
    else:
        param, operator, value = domain

        # if param not in values:
        #     raise UserError(
        #         f"Wrong param name ({param}) for domain {current_name}"
        #         + f"in {parent_name}"
        #     )
        code = f"{param} {operator} {repr(value)}"

        try:
            return safe_eval(code, values)
        except SyntaxError as e:
            raise exceptions.ValidationError(
                f"Domain {domain} is incorrect on {current_name}"
            ) from e


def evaluate_operator(operator, a, b, values, current_name, parent_name):
    if operator == "&":
        return evaluate_domain_operand(
            a, values, current_name, parent_name
        ) & evaluate_domain_operand(b, values, current_name, parent_name)
    if operator == "|":
        return evaluate_domain_operand(
            a, values, current_name, parent_name
        ) | evaluate_domain_operand(b, values, current_name, parent_name)


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    domain = fields.Text(help="Odoo syntax domain only")
    use_formula_compute_qty = fields.Boolean(
        string="Use formula to compute qty", default=False, required=False
    )
    qty_formula = fields.Text(
        string="Quantity formula", help="Formula to compute", default="result = qty"
    )
    condition = fields.Text(help="Comment explaining domain if needed")

    def _create_context(self, input_line):
        context = {
            "qty": self.product_qty,
        }
        params = input_line._get_config_elements()

        for param in params:
            if not input_line._fields[param].relational:
                context[param] = input_line[param]

        return context

    def _run_formula(self, eval_context):
        safe_eval(self.qty_formula.strip(), eval_context, mode="exec", nocopy=True)

    @api.constrains(qty_formula)
    def _check_formula(self):
        pass

    def compute_qty_from_formula(self, input_line):
        eval_context = self._create_context(input_line)
        self._run_formula(eval_context)
        return eval_context.get("result", self.product_qty)

    def goto_configurable_bom_report(self):
        self.ensure_one()
        # TODO add button
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        url = "%s/report/html/mrp_bom_configurable.report_bom_configurable/%s" % (
            base_url,
            self.id,
        )
        return {
            "model": "ir.actions._act_url",
            "name": self.name,
            "url": url,
            "target": "new",
        }

    def check_domain(self, values):
        self.ensure_one()
        if not self.domain:
            return True
        else:
            return check_domain(
                self.domain, values, self.product_id.name, self.bom_id.product_id.name
            )

    def ui_update_domain(self):
        self.ensure_one()
        return {
            "name": _(f"Domain for {self.product_id}"),
            "type": "ir.actions.act_window",
            "res_model": "mrp.bom.line",
            "res_id": self.id,
            "view_mode": "form",
            "target": "current",
        }
