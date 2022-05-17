# Copyright 2022 Trey, Kilobytes de Soluciones - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class QcIssueMakeRepair(models.TransientModel):
    _name = "qc.issue.make.repair"
    _description = "QC Issue Make Repair"

    partner_id = fields.Many2one(
        comodel_name="res.partner",
    )
    item_ids = fields.One2many(
        comodel_name="qc.issue.make.repair.item",
        inverse_name="wiz_id",
    )

    @api.model
    def _prepare_item(self, issue):
        return {
            "qc_issue_id": issue.id,
            "product_id": issue.product_id.id,
            "lot_id": issue.lot_id.id,
            "name": issue.name,
            "product_qty": issue.product_qty,
            "product_uom_id": issue.product_uom.id,
        }

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        Issue = self.env["qc.issue"]
        items = []
        issues = Issue.browse(self.env.context["active_ids"])
        for issue in issues:
            items.append([0, 0, self._prepare_item(issue)])
        res["item_ids"] = items
        return res

    @api.multi
    def make_repair(self):
        Repair = self.env["repair.order"]
        res = []
        action = self.env.ref("repair.action_repair_order_tree")
        action = action.read()[0]
        for issue in self.item_ids:
            if issue.product_qty <= 0.0:
                raise UserError(_("Enter a positive quantity."))
            values = issue._prepare_repair_data()
            repair = Repair.create(values)
            res.append(repair.id)
        if len(res) != 1:
            action["domain"] = [("id", "in", res)]
        elif len(res) == 1:
            view = self.env.ref("repair.view_repair_order_form", False)
            action["views"] = [(view and view.id or False, "form")]
            action["res_id"] = res[0]
        return action


class QcIssueMakeRepairItem(models.TransientModel):
    _name = "qc.issue.make.repair.item"
    _description = "QC Issue Make Repair Item"

    wiz_id = fields.Many2one(
        comodel_name="qc.issue.make.repair",
        string="Wizard",
        required=True,
        ondelete="cascade",
        readonly=True,
    )
    qc_issue_id = fields.Many2one(
        comodel_name="qc.issue",
        string="Quality Issue",
        required=True,
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        related="qc_issue_id.product_id",
        readony=True,
    )
    location_id = fields.Many2one(
        comodel_name="stock.location",
        related="qc_issue_id.location_id",
        readonly=True,
    )
    lot_id = fields.Many2one(
        comodel_name="stock.production.lot",
        related="qc_issue_id.lot_id",
        readonly=True,
        string="Lot/Serial Number",
    )
    name = fields.Char(
        related="qc_issue_id.name",
        readonly=True,
    )
    product_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="UoM",
        readonly=True,
    )
    product_qty = fields.Float(
        string="Quantity to Repair",
        digits=dp.get_precision("Product Unit of Measure"),
    )

    @api.model
    def _prepare_repair_data(self):
        self.ensure_one()
        return {
            "partner_id": self.wiz_id.partner_id.id,
            "address_id": self.wiz_id.partner_id.id,
            "product_id": self.product_id.id,
            "product_uom": self.product_uom_id.id,
            "qc_issue_id": self.qc_issue_id.id,
            "product_qty": self.product_qty,
            "lot_id": self.lot_id.id,
            "location_id": self.location_id.id,
        }
