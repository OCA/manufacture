# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api
from odoo.tools import config


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    def _track_subtype(self, init_values):
        self.ensure_one()
        if "state" in init_values and self.state == "active":
            return self.env.ref("mrp_bom_version.mt_active")
        return super(MrpBom, self)._track_subtype(init_values)

    def _compute_old_versions(self):
        self.ensure_one()
        parent = self.parent_bom
        old_version = self.env["mrp.bom"]
        while parent:
            old_version += parent
            parent = parent.parent_bom
        self.old_versions = old_version

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
    historical_date = fields.Date(string="Historical Date", readonly=True)
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("active", "Active"),
            ("historical", "Historical"),
        ],
        string="State",
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
    # routing_id = fields.Many2one(
    #     readonly=True, states={"draft": [("readonly", False)]}
    # )
    bom_line_ids = fields.One2many(
        readonly=True, states={"draft": [("readonly", False)]}
    )
    message_follower_ids = fields.One2many(states={"historical": [("readonly", True)]})
    message_ids = fields.One2many(states={"historical": [("readonly", True)]})
    version = fields.Integer(
        states={"historical": [("readonly", True)]}, copy=False, default=1
    )
    parent_bom = fields.Many2one(comodel_name="mrp.bom", string="Parent BoM")
    old_versions = fields.Many2many(
        comodel_name="mrp.bom", string="Old Versions", compute="_compute_old_versions"
    )

    def button_draft(self):
        active_draft = (
            self.env["ir.config_parameter"].sudo().get_param("active_draft", False)
        )
        self.write({"active": active_draft, "state": "draft"})

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
        active_draft = (
            self.env["ir.config_parameter"].sudo().get_param("active_draft", False)
        )
        new_bom = self.copy(
            {"version": self.version + 1, "active": active_draft, "parent_bom": self.id}
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

    def search(self, args, offset=0, limit=None, order=None, count=False):
        """Add search argument for field type if the context says so.
        """
        search_state = self.env.context.get("state", False)
        if search_state:
            args += [("state", "=", search_state)]
        return super(MrpBom, self).search(
            args, offset=offset, limit=limit, order=order, count=count
        )

    @api.model
    def _bom_find(self, products, picking_type=None, company_id=False, bom_type=False):
        """ Finds BoM for particular product, picking and company """
        return super(MrpBom, self.with_context(state="active"))._bom_find(
            products=products,
            picking_type=picking_type,
            company_id=company_id,
            bom_type=bom_type,
        )
