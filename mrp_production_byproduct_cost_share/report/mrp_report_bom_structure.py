# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import _, api, models
from odoo.tools import float_round


class ReportBomStructure(models.AbstractModel):
    _inherit = "report.mrp.report_bom_structure"

    @api.model
    def get_byproducts(self, bom_id=False, qty=0, level=0, total=0):
        bom = self.env["mrp.bom"].browse(bom_id)
        lines, dummy = self._get_byproducts_lines(bom, qty, level, total)
        values = {
            "bom_id": bom_id,
            "currency": self.env.company.currency_id,
            "byproducts": lines,
        }
        return self.env.ref(
            "mrp_production_byproduct_cost_share.report_mrp_byproduct_line"
        )._render({"data": values})

    def _get_bom(
        self, bom_id=False, product_id=False, line_qty=False, line_id=False, level=False
    ):
        res = super()._get_bom(bom_id, product_id, line_qty, line_id, level)
        byproducts, byproduct_cost_portion = self._get_byproducts_lines(
            res["bom"], res["bom_qty"], res["level"], res["total"]
        )
        res["byproducts"] = byproducts
        res["cost_share"] = float_round(
            1 - byproduct_cost_portion, precision_rounding=0.0001
        )
        res["bom_cost"] = res["total"] * res["cost_share"]
        res["byproducts_cost"] = sum(byproduct["bom_cost"] for byproduct in byproducts)
        res["byproducts_total"] = sum(
            byproduct["product_qty"] for byproduct in byproducts
        )
        return res

    def _get_bom_lines(self, bom, bom_quantity, product, line_id, level):
        components, total = super()._get_bom_lines(
            bom, bom_quantity, product, line_id, level
        )
        for line in bom.bom_line_ids:
            line_quantity = (bom_quantity / (bom.product_qty or 1.0)) * line.product_qty
            if line._skip_bom_line(product):
                continue
            if line.child_bom_id:
                factor = (
                    line.product_uom_id._compute_quantity(
                        line_quantity, line.child_bom_id.product_uom_id
                    )
                    / line.child_bom_id.product_qty
                )
                sub_total = self._get_price(line.child_bom_id, factor, line.product_id)
                byproduct_cost_share = sum(
                    line.child_bom_id.byproduct_ids.mapped("cost_share")
                )
                if byproduct_cost_share:
                    sub_total_byproducts = float_round(
                        sub_total * byproduct_cost_share / 100,
                        precision_rounding=0.0001,
                    )
                    total -= sub_total_byproducts
        return components, total

    def _get_byproducts_lines(self, bom, bom_quantity, level, total):
        byproducts = []
        byproduct_cost_portion = 0
        company = bom.company_id or self.env.company
        for byproduct in bom.byproduct_ids:
            line_quantity = (
                bom_quantity / (bom.product_qty or 1.0)
            ) * byproduct.product_qty
            cost_share = byproduct.cost_share / 100
            byproduct_cost_portion += cost_share
            price = (
                byproduct.product_id.uom_id._compute_price(
                    byproduct.product_id.with_company(company).standard_price,
                    byproduct.product_uom_id,
                )
                * line_quantity
            )
            byproducts.append(
                {
                    "product_id": byproduct.product_id,
                    "product_name": byproduct.product_id.display_name,
                    "product_qty": line_quantity,
                    "product_uom": byproduct.product_uom_id.name,
                    "product_cost": company.currency_id.round(price),
                    "parent_id": bom.id,
                    "level": level or 0,
                    "bom_cost": company.currency_id.round(total * cost_share),
                    "cost_share": cost_share,
                }
            )
        return byproducts, byproduct_cost_portion

    def _get_price(self, bom, factor, product):
        price = super()._get_price(bom, factor, product)
        for line in bom.bom_line_ids:
            if line._skip_bom_line(product):
                continue
            if line.child_bom_id:
                qty = (
                    line.product_uom_id._compute_quantity(
                        line.product_qty * factor, line.child_bom_id.product_uom_id
                    )
                    / line.child_bom_id.product_qty
                )
                sub_price = self._get_price(line.child_bom_id, qty, line.product_id)
                byproduct_cost_share = sum(
                    line.child_bom_id.byproduct_ids.mapped("cost_share")
                )
                if byproduct_cost_share:
                    sub_price_byproducts = float_round(
                        sub_price * byproduct_cost_share / 100,
                        precision_rounding=0.0001,
                    )
                    price -= sub_price_byproducts
        return price

    # pylint: disable=W0102
    # flake8: noqa:B006
    def _get_pdf_line(
        self, bom_id, product_id=False, qty=1, child_bom_ids=[], unfolded=False
    ):
        data = super()._get_pdf_line(bom_id, product_id, qty, child_bom_ids, unfolded)

        def get_sub_lines(bom, product_id, line_qty, line_id, level):
            # method overriden
            data = self._get_bom(
                bom_id=bom.id,
                product_id=product_id,
                line_qty=line_qty,
                line_id=line_id,
                level=level,
            )
            bom_lines = data["components"]
            lines = []
            for bom_line in bom_lines:
                lines.append(
                    {
                        "name": bom_line["prod_name"],
                        "type": "bom",
                        "quantity": bom_line["prod_qty"],
                        "uom": bom_line["prod_uom"],
                        "prod_cost": bom_line["prod_cost"],
                        "bom_cost": bom_line["total"],
                        "level": bom_line["level"],
                        "code": bom_line["code"],
                        "child_bom": bom_line["child_bom"],
                        "prod_id": bom_line["prod_id"],
                    }
                )
                if bom_line["child_bom"] and (
                    unfolded or bom_line["child_bom"] in child_bom_ids
                ):
                    line = self.env["mrp.bom.line"].browse(bom_line["line_id"])
                    lines += get_sub_lines(
                        line.child_bom_id,
                        line.product_id.id,
                        bom_line["prod_qty"],
                        line,
                        level + 1,
                    )
            if data["operations"]:
                lines.append(
                    {
                        "name": _("Operations"),
                        "type": "operation",
                        "quantity": data["operations_time"],
                        "uom": _("minutes"),
                        "bom_cost": data["operations_cost"],
                        "level": level,
                    }
                )
                for operation in data["operations"]:
                    if unfolded or "operation-" + str(bom.id) in child_bom_ids:
                        lines.append(
                            {
                                "name": operation["name"],
                                "type": "operation",
                                "quantity": operation["duration_expected"],
                                "uom": _("minutes"),
                                "bom_cost": operation["total"],
                                "level": level + 1,
                            }
                        )
            # start of changes
            if data["byproducts"]:
                lines.append(
                    {
                        "name": _("Byproducts"),
                        "type": "byproduct",
                        "uom": False,
                        "quantity": data["byproducts_total"],
                        "bom_cost": data["byproducts_cost"],
                        "level": level,
                    }
                )
                for byproduct in data["byproducts"]:
                    if unfolded or "byproduct-" + str(bom.id) in child_bom_ids:
                        lines.append(
                            {
                                "name": byproduct["product_name"],
                                "type": "byproduct",
                                "quantity": byproduct["product_qty"],
                                "uom": byproduct["product_uom"],
                                "prod_cost": byproduct["product_cost"],
                                "bom_cost": byproduct["bom_cost"],
                                "level": level + 1,
                            }
                        )
            return lines

        bom = self.env["mrp.bom"].browse(bom_id)
        product_id = (
            product_id or bom.product_id.id or bom.product_tmpl_id.product_variant_id.id
        )
        pdf_lines = get_sub_lines(bom, product_id, qty, False, 1)
        data["lines"] = pdf_lines
        return data
