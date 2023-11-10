# Copyright 2020-21 ForgeFlow S.L. (https://www.forgeflow.com)
# - Jordi Ballester Alomar <jordi.ballester@forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import timedelta
from itertools import zip_longest

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools.float_utils import float_compare


class MrpPlannedOrderWizard(models.TransientModel):
    _name = "mrp.planned.order.wizard"
    _description = "MPS Wizard"

    date_start = fields.Date(string="Date From", required=True)
    date_end = fields.Date(string="Date To", required=True)
    date_range_type_id = fields.Many2one(
        string="Date Range Type",
        comodel_name="date.range.type",
        required=True,
    )
    product_mrp_area_ids = fields.Many2many(
        string="Product Parameters", comodel_name="product.mrp.area", required=True
    )

    @api.constrains("date_start", "date_end")
    def _check_start_end_dates(self):
        self.ensure_one()
        if self.date_start > self.date_end:
            raise ValidationError(
                _("The start date cannot be later than the end date.")
            )

    def create_sheet(self):
        self.ensure_one()
        if not self.product_mrp_area_ids:
            raise ValidationError(
                _("You must select at least one Product MRP parameter.")
            )

        # 2d matrix widget need real records to work
        sheet = self.env["mrp.planned.order.sheet"].create(
            {
                "date_start": self.date_start,
                "date_end": self.date_end,
                "date_range_type_id": self.date_range_type_id.id,
                "product_mrp_area_ids": [(6, 0, self.product_mrp_area_ids.ids)],
            }
        )
        sheet._onchange_dates()
        res = {
            "name": _("MPS Sheet"),
            "src_model": "mrp.planned.order.wizard",
            "view_mode": "form",
            "target": "new",
            "res_model": "mrp.planned.order.sheet",
            "res_id": sheet.id,
            "type": "ir.actions.act_window",
        }
        return res


class MprPlannedOrderSheet(models.TransientModel):
    _name = "mrp.planned.order.sheet"
    _description = "MPS Sheet"

    date_start = fields.Date(string="Date From", readonly=True)
    date_end = fields.Date(string="Date to", readonly=True)
    date_range_type_id = fields.Many2one(
        string="Date Range Type",
        comodel_name="date.range.type",
        readonly=True,
    )
    product_mrp_area_ids = fields.Many2many(
        string="Product Parameters", comodel_name="product.mrp.area"
    )
    line_ids = fields.Many2many(
        string="Items", comodel_name="mrp.planned.order.sheet.line"
    )

    @api.onchange("date_start", "date_end", "date_range_type_id")
    def _onchange_dates(self):
        if not all([self.date_start, self.date_end, self.date_range_type_id]):
            return
        ranges = self._get_ranges()
        if not ranges:
            raise UserError(_("There are no date ranges created."))
        lines = []
        for rec in self.product_mrp_area_ids:
            for d_range in ranges:
                items = self.env["mrp.planned.order"].search(
                    [
                        ("product_mrp_area_id", "=", rec.id),
                        ("due_date", ">=", d_range.date_start),
                        ("due_date", "<", d_range.date_end),
                        ("fixed", "=", True),
                    ]
                )
                if items:
                    uom_qty = sum(items.mapped("mrp_qty"))
                    item_ids = items.ids
                else:
                    uom_qty = 0.0
                    item_ids = []
                lines.append(
                    [
                        0,
                        0,
                        self._get_default_sheet_line(d_range, rec, uom_qty, item_ids),
                    ]
                )
        self.line_ids = lines

    def _get_ranges(self):
        domain_1 = [
            "&",
            ("type_id", "=", self.date_range_type_id.id),
            "|",
            "&",
            ("date_start", ">=", self.date_start),
            ("date_start", "<=", self.date_end),
            "&",
            ("date_end", ">=", self.date_start),
            ("date_end", "<=", self.date_end),
        ]
        domain_2 = [
            "&",
            ("type_id", "=", self.date_range_type_id.id),
            "&",
            ("date_start", "<=", self.date_start),
            ("date_end", ">=", self.date_start),
        ]
        domain = expression.OR([domain_1, domain_2])
        ranges = self.env["date.range"].search(domain)
        return ranges

    def _get_default_sheet_line(self, d_range, product_mrp, uom_qty, item_ids):
        name_y = "{} - {}".format(
            product_mrp.display_name, product_mrp.product_id.uom_id.name
        )
        values = {
            "value_x": d_range.name,
            "value_y": name_y,
            "date_range_id": d_range.id,
            "product_mrp_area_id": product_mrp.id,
            "product_qty": uom_qty,
            "mrp_planned_order_ids": [(6, 0, item_ids)],
        }
        return values

    @api.model
    def _prepare_planned_order_data(self, line, qty):
        calendar = line.product_mrp_area_id.mrp_area_id.calendar_id
        due_date = line.date_range_id.date_start
        lt = line.product_mrp_area_id.mrp_lead_time
        due_date_dt = fields.Datetime.from_string(due_date)
        if calendar:
            res = calendar.plan_days(-1 * lt - 1, due_date_dt)
            release_date = res.date()
        else:
            release_date = due_date_dt - timedelta(days=lt)
        return {
            "name": "Planned Order for %s"
            % line.product_mrp_area_id.product_id.display_name,
            "order_release_date": release_date,
            "due_date": due_date,
            "product_mrp_area_id": line.product_mrp_area_id.id,
            "mrp_qty": qty,
            "qty_released": 0.0,
            "mrp_action": line.product_mrp_area_id.supply_method,
            "fixed": True,
        }

    def button_validate(self):
        res_ids = []
        for line in self.line_ids:
            quantities = []
            qty_to_order = line.product_qty
            while qty_to_order > 0.0:
                qty = line.product_mrp_area_id._adjust_qty_to_order(qty_to_order)
                quantities.append(qty)
                qty_to_order -= qty
            rounding = line.product_mrp_area_id.product_id.uom_id.rounding
            for proposed, current in zip_longest(
                quantities, line.mrp_planned_order_ids
            ):
                if not proposed:
                    current.unlink()
                elif not current:
                    data = self._prepare_planned_order_data(line, proposed)
                    item = self.env["mrp.planned.order"].create(data)
                    res_ids.append(item.id)
                elif (
                    float_compare(
                        proposed, current.mrp_qty, precision_rounding=rounding
                    )
                    == 0
                ):
                    res_ids.append(current.id)
                else:
                    current.mrp_qty = proposed
                    res_ids.append(current.id)

        res = {
            "domain": [("id", "in", res_ids)],
            "name": _("Planned Orders"),
            "src_model": "mrp.planned.order.wizard",
            "view_mode": "tree,form,pivot",
            "res_model": "mrp.planned.order",
            "type": "ir.actions.act_window",
        }
        return res


class MprPlannedOrderSheetLine(models.TransientModel):
    _name = "mrp.planned.order.sheet.line"
    _description = "MPS Sheet Line"

    mrp_planned_order_ids = fields.Many2many(comodel_name="mrp.planned.order")
    product_mrp_area_id = fields.Many2one(
        string="Product Parameters", comodel_name="product.mrp.area"
    )
    date_range_id = fields.Many2one(
        comodel_name="date.range",
        string="Date Range",
    )
    value_x = fields.Char(string="Period")
    value_y = fields.Char(string="Product")
    product_qty = fields.Float(string="Quantity", digits="Product UoM")
