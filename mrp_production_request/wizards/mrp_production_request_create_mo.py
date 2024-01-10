# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
import openerp.addons.decimal_precision as dp


class MrpProductionRequestCreateMo(models.TransientModel):
    _name = "mrp.production.request.create.mo"
    _description = "Wizard to create Manufacturing Orders"

    @api.multi
    def compute_product_line_ids(self):
        self.product_line_ids.unlink()
        res = self._prepare_lines()
        product_lines = res[0]
        # workcenter_lines = res[1]  # TODO: expand with workcenter_lines
        for line in product_lines:
            self.env['mrp.production.request.create.mo.line'].create(
                self._prepare_product_line(line))
        # reset workcenter_lines in production order
        # for line in workcenter_lines:
        #     line['production_id'] = production.id
        #     workcenter_line_obj.create(cr, uid, line, context)
        self._get_mo_qty()
        return {"type": "ir.actions.do_nothing"}

    def _prepare_lines(self):
        """Get the components (product_lines) and Work Centers Utilisation
        (workcenter_lines) needed for manufacturing the given a BoM.
        :return: product_lines, workcenter_lines
        """
        bom_obj = self.env['mrp.bom']
        uom_obj = self.env['product.uom']
        bom_point = self.bom_id
        factor = uom_obj._compute_qty(
            self.mrp_production_request_id.product_uom.id, self.pending_qty,
            bom_point.product_uom.id)
        return bom_obj._bom_explode(
            bom_point, self.mrp_production_request_id.product_id,
            factor / bom_point.product_qty,
            routing_id=self.mrp_production_request_id.routing_id.id)

    @api.one
    def _get_mo_qty(self):
        """Propose a qty to create a MO available to produce."""
        bottle_neck = min(self.product_line_ids.mapped('bottle_neck_factor'))
        bottle_neck = max(min(1, bottle_neck), 0)
        self.mo_qty = self.pending_qty * bottle_neck

    mrp_production_request_id = fields.Many2one(
        comodel_name="mrp.production.request", readonly=True)
    bom_id = fields.Many2one(
        related='mrp_production_request_id.bom_id', readonly=True)
    mo_qty = fields.Float(
        string="Quantity",
        digits_compute=dp.get_precision("Product Unit of Measure"))
    pending_qty = fields.Float(
        related="mrp_production_request_id.pending_qty",
        digits_compute=dp.get_precision("Product Unit of Measure"))
    product_uom = fields.Many2one(
        related="mrp_production_request_id.product_uom")
    product_line_ids = fields.One2many(
        comodel_name="mrp.production.request.create.mo.line",
        string="Products needed",
        inverse_name="mrp_production_request_create_mo_id", readonly=True)

    def _prepare_product_line(self, pl):
        return {
            'product_id': pl['product_id'],
            'product_qty': pl['product_qty'],
            'product_uom': pl['product_uom'],
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
            'product_uom': self.product_uom.id,
            'mrp_production_request_id': self.mrp_production_request_id.id,
            'origin': request_id.origin,
            'location_src_id': request_id.location_src_id.id,
            'location_dest_id': request_id.location_dest_id.id,
            'routing_id': request_id.routing_id.id,
            'move_prod_id': request_id.procurement_id.move_dest_id.id or False,
            'date_planned': request_id.date_planned,
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

    @api.one
    def _compute_available_qty(self):
        product_available = self.product_id.with_context(
            location=self.location_id.id)._product_available()[
            self.product_id.id]['qty_available_not_res']
        res = self.product_uom._compute_qty(
            self.product_id.product_tmpl_id.uom_id.id, product_available,
            self.product_uom.id)
        self.available_qty = res

    @api.one
    def _compute_bottle_neck_factor(self):
        if self.product_qty:
            self.bottle_neck_factor = self.available_qty / self.product_qty

    product_id = fields.Many2one(
        comodel_name='product.product', string='Product', required=True)
    product_qty = fields.Float(
        string='Quantity Required', required=True,
        digits_compute=dp.get_precision('Product Unit of Measure'))
    product_uom = fields.Many2one(
        comodel_name='product.uom', string='UoM', required=True)
    mrp_production_request_create_mo_id = fields.Many2one(
        comodel_name='mrp.production.request.create.mo')
    available_qty = fields.Float(
        string='Quantity Available', compute=_compute_available_qty,
        digits_compute=dp.get_precision('Product Unit of Measure'))
    bottle_neck_factor = fields.Float(compute=_compute_bottle_neck_factor)
    location_id = fields.Many2one(comodel_name='stock.location',
                                  required=True)
