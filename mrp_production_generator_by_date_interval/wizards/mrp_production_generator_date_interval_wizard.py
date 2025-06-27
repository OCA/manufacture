# Copyright 2025 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, time

import pytz
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MrpProductionGeneratorDateIntervalWizard(models.TransientModel):
    _name = "mrp.production.generator.date.interval.wizard"
    _description = "Wizard to generate MRP Productions by Date Interval"

    product_id = fields.Many2one(
        "product.product",
        required=True,
        domain="[('bom_ids', '!=', False), ('bom_ids.type', '=', 'normal')]",
    )
    bom_id = fields.Many2one(
        "mrp.bom",
        "BOM Components",
        required=True,
        domain="""[
        '&',
            '|',
                ('company_id', '=', False),
                ('company_id', '=', company_id),
            '&',
                '|',
                    ('product_id','=',product_id),
                    '&',
                        ('product_tmpl_id.product_variant_ids','=',product_id),
                        ('product_id','=',False),
        ('type', '=', 'normal')]""",
    )
    period_date_start = fields.Date("Period Start Date", required=True)
    period_date_end = fields.Date("Period End Date", required=True)
    hour_start = fields.Float("Start Hour", required=True)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )

    @api.onchange("product_id")
    def _onchange_product_id(self):
        if not self.product_id:
            self.bom_id = False
        elif (
            not self.bom_id
            or (self.bom_id.product_id and self.bom_id.product_id != self.product_id)
            or self.product_id not in self.bom_id.product_tmpl_id.product_variant_ids
        ):
            self.bom_id = self.product_id.bom_ids.filtered(
                lambda bom: bom.type == "normal"
            )[:1]

    @api.onchange("bom_id")
    def _onchange_bom_id(self):
        if not self.product_id and self.bom_id:
            self.product_id = (
                self.bom_id.product_id
                or self.bom_id.product_tmpl_id.product_variant_ids[:1]
            )

    @api.constrains("period_date_start", "period_date_end")
    def _check_period_date_end(self):
        for wiz in self:
            if wiz.period_date_end < wiz.period_date_start:
                raise UserError(_("Period Start Date must be before Period End Date"))

    def action_create_production(self):
        self.ensure_one()
        current_date = self.period_date_start
        hour = int(self.hour_start)
        minutes = int(round((self.hour_start - hour) * 60))
        start_time = time(hour, minutes)
        user_tz = self.env.user.tz or "UTC"
        tz = pytz.timezone(user_tz)
        res_ids = []
        while current_date <= self.period_date_end:
            local_datetime = datetime.combine(current_date, start_time)
            localized_datetime = tz.localize(local_datetime)
            planned_datetime = localized_datetime.astimezone(pytz.utc)
            mrp_production = self.env["mrp.production"].create(
                {
                    "date_start": fields.Datetime.to_string(planned_datetime),
                    "product_id": self.product_id.id,
                    "bom_id": self.bom_id.id,
                    "product_uom_id": self.product_id.uom_id.id,
                    "origin": _("Created using Production Generator Wizard"),
                    "company_id": self.company_id.id,
                }
            )
            res_ids.append(mrp_production.id)
            current_date += relativedelta(days=1)
        action = self.env["ir.actions.actions"]._for_xml_id("mrp.mrp_production_action")
        return dict(action, domain=[("id", "in", res_ids)])
