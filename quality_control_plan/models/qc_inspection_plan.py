# Copyright 2019 Marcelo Frare (Ass. PNLUG - Gruppo Odoo <http://odoo.pnlug.it>)
# Copyright 2019 Stefano Consolaro (Ass. PNLUG - Gruppo Odoo <http://odoo.pnlug.it>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class QcInspection(models.Model):
    """
    Extends inspection with:
        - plan control
        - nonconformity relations
        - method to fill inspection with control plan data
        - method create nonconformity from inspection
    """

    _inherit = ["qc.inspection"]

    # new fields
    # the control plan to be used
    plan_id = fields.Many2one("qc.plan", "Control Plan")
    # quantity to be checked
    qty_checked = fields.Float("Quantity checked")
    # nonconformity reference
    inspection_ids = fields.One2many(
        "mgmtsystem.nonconformity", "inspection_id", "Nonconformity"
    )

    @api.model
    def _new_record_fill(self, plan_id, new_record):
        """
        Used to simplify create() method
        """
        if plan_id:
            # assigns plan to be used
            new_record.plan_id = plan_id

            if new_record.plan_id.free_pass:
                # for free pass doesn't check product
                new_record.qty_checked = 0

            else:
                # gets check informations from levels
                qty_related = self.env["qc.level"].search(
                    [
                        ("plan_id", "=", plan_id.id),
                        ("qty_received", "<", new_record.qty),
                    ],
                    limit=1,
                    order="qty_received desc",
                )
                # assigns qty to check
                if qty_related:
                    if qty_related.chk_type == "percent":
                        # as percent of qty to check
                        new_record.qty_checked = int(
                            new_record.qty * qty_related.qty_checked / 100
                        )
                    else:
                        # as absolute value
                        new_record.qty_checked = qty_related.qty_checked

                # verifies if enough pcs to check
                if new_record.qty_checked > new_record.qty:
                    new_record.qty_checked = new_record.qty

                # checks and fix absolute minimum value lower to 1
                if new_record.qty_checked < 1:
                    new_record.qty_checked = 1

        return new_record

    @api.model
    def create(self, values):
        """
        Extends inspection method by integrating logic to determine the control plan
        to be used and the calculation of the quantity to be checked
        """

        # calls original method
        new_record = super(QcInspection, self).create(values)

        # gets product of the inspection
        product_id = new_record.product_id

        # gets partner from picking if exists
        if new_record.picking_id:
            partner_id = (
                self.env["stock.picking"]
                .search([("id", "=", new_record.picking_id.id)], limit=1)
                .partner_id.id
            )
        else:
            partner_id = False

        # temporary presetted solutions
        solution_art_prt = ""  # plan for product (article) and partner
        solution_cat_prt = ""  # plan for product category and partner
        solution_art = ""  # plan for product (article)
        solution_cat = ""  # plan for product category
        solution_prt = ""  # plan for partner

        # tries to get plan for product and partner
        solution_art_prt = self.env["qc.trigger.product_template_line"].search(
            [
                ("product_template", "=", product_id.product_tmpl_id.id),
                ("partners", "!=", False),
                ("partners", "=", partner_id),
            ],
            limit=1,
        )

        if len(solution_art_prt) == 0:
            # tries to gets plan for category and partner
            solution_cat_prt = self.env["qc.trigger.product_category_line"].search(
                [
                    ("product_category", "=", product_id.categ_id.id),
                    ("partners", "!=", False),
                    ("partners", "=", partner_id),
                ],
                limit=1,
            )

        if len(solution_art_prt) + len(solution_cat_prt) == 0:
            # tries to get plan for product
            solution_art = self.env["qc.trigger.product_template_line"].search(
                [
                    ("product_template", "=", product_id.product_tmpl_id.id),
                    ("partners", "=", False),
                ],
                limit=1,
            )

        if len(solution_art_prt) + len(solution_cat_prt) + len(solution_art) == 0:
            # tries to get plan for category
            solution_cat = self.env["qc.trigger.product_category_line"].search(
                [
                    ("product_category", "=", product_id.categ_id.id),
                    ("partners", "=", False),
                ],
                limit=1,
            )

        if (
            len(solution_art_prt)
            + len(solution_cat_prt)
            + len(solution_art)
            + len(solution_cat)
            == 0
        ):
            # tries to get plan for partner
            solution_prt = self.env["qc.trigger.partner_line"].search(
                [("partner", "=", partner_id)], limit=1
            )

        # gets the plan from the first positive try
        if len(solution_art_prt):
            plan_id = solution_art_prt.plan_id
        elif len(solution_cat_prt):
            plan_id = solution_cat_prt.plan_id
        elif len(solution_art):
            plan_id = solution_art.plan_id
        elif len(solution_cat):
            plan_id = solution_cat.plan_id
        elif len(solution_prt):
            plan_id = solution_prt.plan_id
        else:
            new_record.qty_checked = "1"
            new_record.plan_id = ""
            return new_record

        new_record = self._new_record_fill(plan_id, new_record)

        return new_record

    def create_nonconformity(self, **kwargs):
        """
        Opens nonconformity form view prefilled with inspection data
        """

        # gets partner if exists
        if self.picking_id.partner_id.id:
            partner = self.picking_id.partner_id.id
        else:
            partner = False

        tmp_form_name = "mgmtsystem_nonconformity.view_mgmtsystem_nonconformity_form"
        return {
            # opens nonconformity form view
            "name": _("Create Nonconformity on not compliant Inspection"),
            "view_type": "form",
            "view_mode": "form",
            "res_model": "mgmtsystem.nonconformity",
            "view_id": self.env.ref(tmp_form_name).id,
            "type": "ir.actions.act_window",
            # fills fields with inspection data
            "context": {
                "default_name": _("Inspection not compliant"),
                "default_product_id": self.product_id.id,
                "default_partner_id": partner,
                "default_qty_checked": self.qty_checked,
                "default_inspection_id": self.id,
            },
            "target": "new",
        }
