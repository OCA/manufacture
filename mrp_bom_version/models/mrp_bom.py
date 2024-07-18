# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import _, api, fields, models
from odoo.models import expression
from odoo.tools import config
from odoo.tools.safe_eval import safe_eval


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    def _compute_num_old_versions(self):
        for bom in self:
            old_versions = bom._catch_old_versions()
            bom.num_old_versions = len(old_versions)

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
        default=_default_active,
        readonly=True,
        copy=False,
        states={"draft": [("readonly", False)]},
    )
    historical_date = fields.Date(readonly=True, copy=False)
    state = fields.Selection(
        selection=[
            ("draft", _("Draft")),
            ("active", _("Active")),
            ("historical", _("Historical")),
        ],
        index=True,
        readonly=True,
        default=_default_state,
        copy=False,
        tracking=True,
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
    version = fields.Integer(
        states={"historical": [("readonly", True)]},
        copy=False,
        default=1,
    )
    parent_bom = fields.Many2one(
        string="Parent BoM", comodel_name="mrp.bom", copy=False
    )
    num_old_versions = fields.Integer(
        string="Num. Old Versions",
        comodel_name="mrp.bom",
        compute="_compute_num_old_versions",
    )

    def _track_subtype(self, init_values):
        self.ensure_one()
        if "state" in init_values and self.state == "active":
            return self.env.ref("mrp_bom_version.mrp_bom_active")
        return super()._track_subtype(init_values)

    def button_draft(self):
        bom_active_draft = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("mrp_bom_version.bom_active_draft", False)
        )
        self.write(
            {
                "active": bom_active_draft,
                "state": "draft",
            }
        )

    def button_new_version(self):
        self.ensure_one()
        new_bom = self._copy_bom()
        self.button_historical()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "mrp.mrp_bom_form_action"
        )
        domain = expression.AND(
            [
                [("id", "in", new_bom.ids)],
                safe_eval(action.get("domain") or "[]"),
            ]
        )
        action.update({"domain": domain})
        return action

    def _copy_bom(self):
        bom_active_draft = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("mrp_bom_version.bom_active_draft", False)
        )
        new_bom = self.copy(
            {
                "version": self.version + 1,
                "active": bom_active_draft,
                "parent_bom": self.id,
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
        search_state = False
        if "state" in self.env.context and self.env.context.get("state", False):
            search_state = self.env.context.get("state")
        if search_state:
            args += [("state", "=", search_state)]
        return super().search(
            args, offset=offset, limit=limit, order=order, count=count
        )

    @api.model
    def _bom_find(self, products, picking_type=None, company_id=False, bom_type=False):
        bom = super(MrpBom, self.with_context(state="active"))._bom_find(
            products=products,
            picking_type=picking_type,
            company_id=company_id,
            bom_type=bom_type,
        )
        return bom

    def button_show_old_versions(self):
        self.ensure_one()
        old_versions = self._catch_old_versions()
        action = self.env.ref("mrp.mrp_bom_form_action")
        action_dict = action.read()[0] if action else {}
        domain = expression.AND(
            [[("id", "in", old_versions.ids)], safe_eval(action.domain or "[]")]
        )
        action_dict.update({"domain": domain})
        return action_dict

    def _catch_old_versions(self):
        old_versions = self.env["mrp.bom"]
        parent = self.parent_bom
        while parent:
            old_versions += parent
            parent = parent.parent_bom
        return old_versions
