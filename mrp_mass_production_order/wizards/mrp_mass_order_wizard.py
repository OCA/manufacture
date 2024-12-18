# Copyright 2024 Antoni Marroig(APSL-Nagarro)<amarroig@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import _, api, fields, models


class MassMrpProductionOrderEntryWizard(models.TransientModel):
    _name = "mrp.mass.production.order.entry.wizard"
    _description = "MRP production order entries"

    product_id = fields.Many2one(
        "product.product",
        "Manufactured Product",
        domain="[('type', 'in', ['product', 'consu'])]",
        required=True,
    )
    product_qty = fields.Float(
        "Manufactured Quantity",
        digits="Product Unit of Measure",
        required=True,
        default=1,
    )
    product_uom_id = fields.Many2one(
        "uom.uom",
        "Product Unit of Measure",
        required=True,
        store=True,
        readonly=False,
        compute="_compute_uom_id",
        precompute=True,
        domain="[('category_id', '=', product_uom_category_id)]",
    )
    product_uom_category_id = fields.Many2one(related="product_id.uom_id.category_id")
    mrp_production_order_entry_id = fields.Many2one(
        "mrp.mass.production.order.wizard", "MRP production order entry"
    )
    bom_id = fields.Many2one(
        "mrp.bom",
        "Bill of Material",
        domain="""[
            '&',
                '|',
                    ('product_tmpl_id','=',product_id),
                    '&',
                        ('product_id.product_tmpl_id.product_variant_ids','=',product_id),
                        ('product_id','=',False),
        ('type', '=', 'normal')]""",
        compute="_compute_bom_id",
        precompute=True,
        readonly=False,
        store=True,
        help="Bills of Materials, also called recipes, "
        "are used to autocomplete components and work order instructions.",
    )
    tag_ids = fields.Many2many(
        "mrp.tag",
        compute="_compute_tag_ids",
        precompute=True,
        readonly=False,
        store=True,
        string="Tags",
    )
    product_consumed_id = fields.Many2one(
        "product.product",
        "Consumed Product",
        domain="[('type', 'in', ['product', 'consu']), ('id', '!=', product_id)]",
    )
    quantity = fields.Float(
        "Consumed Quantity", digits="Product Unit of Measure", default=1
    )

    @api.depends("bom_id", "product_id")
    def _compute_uom_id(self):
        for production in self:
            if production.bom_id and production._origin.bom_id != production.bom_id:
                production.product_uom_id = production.bom_id.product_uom_id
            elif production.product_id:
                production.product_uom_id = production.product_id.uom_id
            else:
                production.product_uom_id = False

    @api.depends("product_id", "mrp_production_order_entry_id.picking_type_id")
    def _compute_bom_id(self):
        for mo in self:
            if not mo.product_id and not mo.bom_id:
                mo.bom_id = False
                continue
            bom = (
                self.env["mrp.bom"]
                .with_context(active_test=True)
                ._bom_find(
                    mo.product_id,
                    picking_type=mo.mrp_production_order_entry_id.picking_type_id,
                    company_id=mo.mrp_production_order_entry_id.company_id.id,
                    bom_type="normal",
                )[mo.product_id]
            )
            mo.bom_id = bom.id or False

    @api.depends("product_id")
    def _compute_tag_ids(self):
        for record in self:
            record.tag_ids = record.mrp_production_order_entry_id.tag_ids


class MassMrpProductionOrderWizard(models.TransientModel):
    _name = "mrp.mass.production.order.wizard"
    _description = "Multiple MRP production order"

    @api.model
    def _get_default_picking_type_id(self):
        return self.env["stock.picking.type"].search(
            [
                ("code", "=", "mrp_operation"),
            ],
            limit=1,
        )

    mrp_production_order_entries = fields.One2many(
        "mrp.mass.production.order.entry.wizard",
        "mrp_production_order_entry_id",
        "MRP production order entries",
        change_default=True,
    )
    location_src_id = fields.Many2one(
        "stock.location",
        "Components Location",
        compute="_compute_locations",
        store=True,
        readonly=False,
        required=True,
        precompute=True,
        domain="[('usage','=','internal')]",
        help="Location where the system will look for components.",
    )
    location_dest_id = fields.Many2one(
        "stock.location",
        "Finished Products Location",
        compute="_compute_locations",
        readonly=False,
        store=True,
        required=True,
        precompute=True,
        domain="[('usage','=','internal')]",
        help="Location where the system will stock the finished products.",
    )
    picking_type_id = fields.Many2one(
        "stock.picking.type",
        "Operation Type",
        default=_get_default_picking_type_id,
        domain="[('code', '=', 'mrp_operation')]",
        required=True,
    )
    company_id = fields.Many2one(
        "res.company", "Company", default=lambda self: self.env.company, required=True
    )
    produce_all = fields.Boolean(
        default=True,
        help="Check it if all orders have been produced "
        "otherwise they will be confirmed",
    )
    with_bom = fields.Boolean(
        default=True,
        help="Check this if you want to assign a bill of materials, "
        "otherwise products by line.",
    )
    tag_ids = fields.Many2many(
        "mrp.tag",
        string="Tags",
    )

    @api.depends("picking_type_id")
    def _compute_locations(self):
        for production in self:
            if (
                not production.picking_type_id.default_location_src_id
                or not production.picking_type_id.default_location_dest_id
            ):
                company_id = (
                    production.company_id.id
                    if (
                        production.company_id
                        and production.company_id in self.env.companies
                    )
                    else self.env.company.id
                )
                fallback_loc = (
                    self.env["stock.warehouse"]
                    .search([("company_id", "=", company_id)], limit=1)
                    .lot_stock_id
                )
            production.location_src_id = (
                production.picking_type_id.default_location_src_id.id or fallback_loc.id
            )
            production.location_dest_id = (
                production.picking_type_id.default_location_dest_id.id
                or fallback_loc.id
            )

    def get_production_location(self, product_id):
        if not self.company_id:
            return
        location_by_company = self.env["stock.location"]._read_group(
            [("company_id", "in", self.company_id.ids), ("usage", "=", "production")],
            ["company_id"],
            ["id:array_agg"],
        )
        location_by_company = {company.id: ids for company, ids in location_by_company}
        prod_loc = product_id.with_company(self.company_id).property_stock_production
        comp_locs = location_by_company.get(self.company_id.id)
        return prod_loc or (comp_locs and comp_locs[0])

    def action_create(self):
        mrp_ids = []
        for entry in self.mrp_production_order_entries:
            mrp = self.env["mrp.production"].create(
                {
                    "product_id": entry.product_id.id,
                    "product_qty": entry.product_qty,
                    "picking_type_id": self.picking_type_id.id,
                    "location_src_id": self.location_src_id.id,
                    "location_dest_id": self.location_dest_id.id,
                    "product_uom_id": entry.product_uom_id.id,
                    "tag_ids": entry.tag_ids,
                    "bom_id": entry.bom_id.id if self.with_bom else False,
                }
            )
            if not self.with_bom and entry.product_consumed_id:
                mrp.move_raw_ids = [
                    (
                        0,
                        0,
                        {
                            "location_id": self.location_src_id.id,
                            "location_dest_id": self.get_production_location(
                                entry.product_consumed_id
                            ).id,
                            "product_id": entry.product_consumed_id.id,
                            "picked": True,
                            "product_uom_qty": entry.quantity,
                            "name": (
                                "Transfer to Production/"
                                f"{entry.product_consumed_id.name}"
                            ),
                            "move_line_ids": [
                                (
                                    0,
                                    0,
                                    {
                                        "company_id": self.company_id.id,
                                        "product_id": entry.product_consumed_id.id,
                                        "quantity": entry.quantity,
                                    },
                                )
                            ],
                        },
                    )
                ]
            mrp.button_mark_done() if self.produce_all else mrp.action_confirm()
            mrp_ids.append(mrp.id)
        return {
            "name": _("MRP Production Orders Created"),
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "mrp.production",
            "domain": [("id", "in", mrp_ids)],
        }

    @api.onchange("tag_ids")
    def onchange_tag_ids(self):
        for entry in self.mrp_production_order_entries:
            entry.tag_ids = self.tag_ids
