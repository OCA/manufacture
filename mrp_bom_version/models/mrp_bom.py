# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models
from odoo.tools import config


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    def _compute_old_versions(self):
        for bom in self:
            previous = bom.previous_bom_id
            old_version = self.env["mrp.bom"]
            while previous:
                old_version |= previous
                previous = previous.previous_bom_id
            bom.old_versions = [(6, 0, old_version.ids)]

    def _default_active(self):
        """Needed for preserving normal flow when testing other modules."""
        res = False
        if config["test_enable"]:
            res = not bool(self.env.context.get("test_mrp_bom_version"))
        return res

    def _default_state(self):
        """Needed for preserving normal flow when testing other modules."""
        res = "draft"
        if config["test_enable"] and not self.env.context.get("test_mrp_bom_version"):
            res = "active"
        return res

    active = fields.Boolean(
        default=_default_active, readonly=True, states={"draft": [("readonly", False)]}
    )
    historical_date = fields.Date(readonly=True, copy=False)
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("active", "Active"),
            ("historical", "Historical"),
        ],
        string="Status",
        index=True,
        readonly=True,
        default=_default_state,
        copy=False,
    )
    product_tmpl_id = fields.Many2one(
        readonly=True, states={"draft": [("readonly", False)]}
    )
    product_id = fields.Many2one(readonly=True, states={"draft": [("readonly", False)]})
    product_qty = fields.Float(readonly=True, states={"draft": [("readonly", False)]})
    code = fields.Char(states={"historical": [("readonly", True)]})
    type = fields.Selection(states={"historical": [("readonly", True)]})
    company_id = fields.Many2one(states={"historical": [("readonly", True)]})
    product_uom_id = fields.Many2one(states={"historical": [("readonly", True)]})
    bom_line_ids = fields.One2many(
        readonly=True, states={"draft": [("readonly", False)]}
    )
    byproduct_ids = fields.One2many(
        readonly=True, states={"draft": [("readonly", False)]}
    )
    sequence = fields.Integer(states={"historical": [("readonly", True)]})
    operation_ids = fields.One2many(
        readonly=True, states={"draft": [("readonly", False)]}
    )
    ready_to_produce = fields.Selection(states={"historical": [("readonly", True)]})
    picking_type_id = fields.Many2one(states={"historical": [("readonly", True)]})
    consumption = fields.Selection(states={"historical": [("readonly", True)]})
    version = fields.Integer(
        states={"historical": [("readonly", True)]}, copy=False, default=1
    )
    previous_bom_id = fields.Many2one(
        comodel_name="mrp.bom", string="Previous BoM", copy=False
    )
    old_versions = fields.Many2many(
        comodel_name="mrp.bom", compute="_compute_old_versions"
    )

    def _track_subtype(self, init_values):
        if "state" in init_values and self.state == "active":
            return self.env.ref("mrp_bom_version.mt_active")
        return super()._track_subtype(init_values)

    def button_draft(self):
        get_param = self.env["ir.config_parameter"].sudo().get_param
        active_draft = get_param("mrp_bom_version.active_draft")
        self.write(
            {
                "active": active_draft,
                "state": "draft",
            }
        )

    def button_new_version(self):
        self.ensure_one()
        new_bom = self._copy_bom()
        self.button_historical()
        return {
            "type": "ir.actions.act_window",
            "view_type": "form, tree",
            "view_mode": "form",
            "res_model": "mrp.bom",
            "res_id": new_bom.id,
            "target": "current",
        }

    def _copy_bom(self):
        get_param = self.env["ir.config_parameter"].sudo().get_param
        active_draft = get_param("mrp_bom_version.active_draft")
        new_bom = self.copy(
            {
                "version": self.version + 1,
                "active": active_draft,
                "previous_bom_id": self.id,
            }
        )
        return new_bom

    def button_activate(self):
        self.write({"active": True, "state": "active"})

    def button_historical(self):
        self.write(
            {
                "active": False,
                "state": "historical",
                "historical_date": fields.Date.today(),
            }
        )

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """Add search argument for field type if the context says so. This
        should be in old API because context argument is not the last one.
        """
        search_state = self.env.context.get("state", False)
        if search_state:
            args += [("state", "=", search_state)]
        return super().search(
            args,
            offset=offset,
            limit=limit,
            order=order,
            count=count,
        )

    @api.model
    def _bom_find(self, products, picking_type=None, company_id=False, bom_type=False):
        """Find the first BoM for each products

        :param products: `product.product` recordset
        :return: One bom (or empty recordset `mrp.bom` if none find)
                 by product (`product.product` record)
        :rtype: defaultdict(`lambda: self.env['mrp.bom']`)
        """
        bom_id = super(MrpBom, self.with_context(state="active"))._bom_find(
            products,
            picking_type=picking_type,
            company_id=company_id,
            bom_type=bom_type,
        )
        return bom_id
