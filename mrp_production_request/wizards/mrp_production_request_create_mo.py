# Copyright 2017-18 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError


class MrpProductionRequestCreateMo(models.TransientModel):
    _name = "mrp.production.request.create.mo"
    _description = "Wizard to create Manufacturing Orders"

    @api.multi
    def compute_product_line_ids(self):
        self.product_line_ids.unlink()
        res = self._prepare_lines()
        product_lines = res[1]
        for line in product_lines:
            self.env['mrp.production.request.create.mo.line'].create(
                self._prepare_product_line(line))
        self._get_mo_qty()
        return {"type": "ir.actions.do_nothing"}

    def _prepare_lines(self):
        """Get the components (product_lines) needed for manufacturing the
        given a BoM.
        :return: boms_done, lines_done
        """
        bom_point = self.bom_id
        factor = self.mrp_production_request_id.product_uom_id.\
            _compute_quantity(self.pending_qty, bom_point.product_uom_id)
        return bom_point.explode(
            self.mrp_production_request_id.product_id,
            factor / bom_point.product_qty)

    @api.multi
    def _get_mo_qty(self):
        """Propose a qty to create a MO available to produce."""
        for rec in self:
            bottle_neck = min(rec.product_line_ids.mapped(
                'bottle_neck_factor'))
            bottle_neck = max(min(1, bottle_neck), 0)
            rec.mo_qty = rec.pending_qty * bottle_neck

    mrp_production_request_id = fields.Many2one(
        comodel_name="mrp.production.request", readonly=True)
    bom_id = fields.Many2one(
        related='mrp_production_request_id.bom_id', readonly=True)
    mo_qty = fields.Float(
        string="Quantity",
        digits=dp.get_precision("Product Unit of Measure"))
    pending_qty = fields.Float(
        related="mrp_production_request_id.pending_qty",
        digits=dp.get_precision("Product Unit of Measure"))
    product_uom_id = fields.Many2one(
        related="mrp_production_request_id.product_uom_id")
    product_line_ids = fields.One2many(
        comodel_name="mrp.production.request.create.mo.line",
        string="Products needed",
        inverse_name="mrp_production_request_create_mo_id", readonly=True)

    @api.model
    def default_get(self, fields):
        rec = super(MrpProductionRequestCreateMo, self).default_get(fields)
        active_ids = self._context.get('active_ids')
        if not active_ids:
            raise UserError(_(
                "Programming error: wizard action executed without "
                "active_ids in context."))
        rec['mrp_production_request_id'] = active_ids[0]
        return rec

    def _prepare_product_line(self, pl):
        return {
            'product_id': pl[0].product_id.id,
            'product_qty': pl[1]['qty'],
            'product_uom_id': pl[0].product_uom_id.id,
            'mrp_production_request_create_mo_id': self.id,
            'location_id': self.mrp_production_request_id.location_src_id.id,
        }

    @api.multi
    def _prepare_manufacturing_order(self):
        self.ensure_one()
        request_id = self.mrp_production_request_id
        return {
            'product_id': request_id.product_id.id,
            'bom_id': request_id.bom_id.id,
            'product_qty': self.mo_qty,
            'product_uom_id': self.product_uom_id.id,
            'mrp_production_request_id': self.mrp_production_request_id.id,
            'origin': request_id.origin,
            'location_src_id': request_id.location_src_id.id,
            'location_dest_id': request_id.location_dest_id.id,
            'picking_type_id': request_id.picking_type_id.id,
            'routing_id': request_id.routing_id.id,
            'date_planned_start': request_id.date_planned_start,
            'date_planned_finished': request_id.date_planned_finished,
            'procurement_group_id': request_id.procurement_group_id.id,
            'propagate': request_id.propagate,
            'company_id': request_id.company_id.id,
        }

    @api.multi
    def create_mo(self):
        self.ensure_one()
        vals = self._prepare_manufacturing_order()
        mo = self.env['mrp.production'].create(vals)
        # Open resulting MO:
        action = self.env.ref('mrp.mrp_production_action').read()[0]
        res = self.env.ref('mrp.mrp_production_form_view')
        action.update({
            'res_id': mo and mo.id,
            'views': [(res and res.id or False, 'form')],
        })
        return action


class MrpProductionRequestCreateMoLine(models.TransientModel):
    _name = "mrp.production.request.create.mo.line"

    @api.multi
    def _compute_available_qty(self):
        for rec in self:
            product_available = rec.product_id.with_context(
                location=rec.location_id.id).\
                _compute_product_available_not_res_dict()[
                rec.product_id.id]['qty_available_not_res']
            res = rec.product_id.product_tmpl_id.uom_id._compute_quantity(
                product_available, rec.product_uom_id)
            rec.available_qty = res

    @api.multi
    def _compute_bottle_neck_factor(self):
        for rec in self:
            if rec.product_qty:
                rec.bottle_neck_factor = rec.available_qty / rec.product_qty

    product_id = fields.Many2one(
        comodel_name='product.product', string='Product', required=True)
    product_qty = fields.Float(
        string='Quantity Required', required=True,
        digits=dp.get_precision('Product Unit of Measure'))
    product_uom_id = fields.Many2one(
        comodel_name='product.uom', string='UoM', required=True)
    mrp_production_request_create_mo_id = fields.Many2one(
        comodel_name='mrp.production.request.create.mo')
    available_qty = fields.Float(
        string='Quantity Available', compute=_compute_available_qty,
        digits=dp.get_precision('Product Unit of Measure'))
    bottle_neck_factor = fields.Float(compute=_compute_bottle_neck_factor)
    location_id = fields.Many2one(comodel_name='stock.location',
                                  required=True)
