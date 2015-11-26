# -*- coding: utf-8 -*-
# (c) 2015 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models, tools, _
from openerp.exceptions import Warning as UserError
from openerp.addons.product import _common


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.model
    def _factor(self, factor, product_efficiency, product_rounding):
        factor = factor / (product_efficiency or 1.0)
        factor = _common.ceiling(factor, product_rounding)
        if factor < product_rounding:
            factor = product_rounding
        return factor

    @api.multi
    def _prepare_wc_line(self, wc_use, level=0, factor=1):
        self.ensure_one()
        wc = wc_use.workcenter_id
        d, m = divmod(factor, wc_use.workcenter_id.capacity_per_cycle)
        mult = (d + (m and 1.0 or 0.0))
        cycle = mult * wc_use.cycle_nbr
        return {
            'name': (tools.ustr(wc_use.name) + ' - ' +
                     tools.ustr(self.product_tmpl_id.name_get()[0][1])),
            'workcenter_id': wc.id,
            'sequence': level + (wc_use.sequence or 0),
            'cycle': cycle,
            'hour': float(
                wc_use.hour_nbr * mult +
                (wc.time_start or 0.0) +
                (wc.time_stop or 0.0) +
                cycle * (wc.time_cycle or 0.0) * (wc.time_efficiency or 1.0)),
        }

    @api.model
    def _prepare_consume_line(self, bom_line, quantity, factor=1):
        uos_qty = (bom_line.product_uos and
                   self._factor(
                       bom_line.product_uos_qty * factor,
                       bom_line.product_efficiency, bom_line.product_rounding))
        return {
            'name': bom_line.product_id.name,
            'product_id': bom_line.product_id.id,
            'product_qty': quantity,
            'product_uom': bom_line.product_uom.id,
            'product_uos_qty': uos_qty or False,
            'product_uos': bom_line.product_uos.id,
        }

    @api.model
    def _bom_find_prepare(self, bom_line, properties=None):
        return self._bom_find(
            product_id=bom_line.product_id.id, properties=properties)

    @api.model
    def _get_bom_product_name(self, bom_line):
        return bom_line.product_id.name_get()[0][1]

    @api.v7
    def _bom_explode(self, cr, uid, bom, product, factor, properties=None,
                     level=0, routing_id=False, previous_products=None,
                     master_bom=None, context=None):
        """ Finds Products and Work Centers for related BoM for manufacturing
        order.

        Verbatim copy of core method extracting the hooks already merged on
        v9 branch.

        @param bom: BoM of particular product template.
        @param product: Select a particular variant of the BoM. If False use
        BoM without variants.
        @param factor: Factor represents the quantity, but in UoM of the BoM,
        taking into account the numbers produced by the BoM
        @param properties: A List of properties Ids.
        @param level: Depth level to find BoM lines starts from 10.
        @param previous_products: List of product previously use by bom
        explore to avoid recursion
        @param master_bom: When recursion, used to display the name of the
        master bom
        @return: result: List of dictionaries containing product details.
                 result2: List of dictionaries containing Work Center details.
        """
        return bom._bom_explode(
            product, factor, properties=properties, level=level,
            routing_id=routing_id, previous_products=previous_products,
            master_bom=master_bom)

    @api.v8
    def _bom_explode(self, product, factor, properties=None, level=0,
                     routing_id=False, previous_products=None,
                     master_bom=None):
        self.ensure_one()
        bom = self
        uom_obj = self.env["product.uom"]
        routing_obj = self.env['mrp.routing']
        master_bom = master_bom or bom
        factor = self._factor(
            factor, bom.product_efficiency, bom.product_rounding)
        result = []
        result2 = []
        routing = ((routing_id and routing_obj.browse(routing_id)) or
                   bom.routing_id or False)
        if routing:
            for wc_use in routing.workcenter_lines:
                result2.append(self._prepare_wc_line(
                    wc_use, level=level, factor=factor))
        for bom_line_id in bom.bom_line_ids:
            if self._skip_bom_line(bom_line_id, product):
                continue
            if (set(map(int, bom_line_id.property_ids or [])) -
                    set(properties or [])):
                continue
            product_tmpl_id = bom_line_id.product_id.product_tmpl_id.id
            if (previous_products and
                    product_tmpl_id in previous_products):
                raise UserError(
                    _('BoM "%s" contains a BoM line with a product recursion: '
                      '"%s".') % (master_bom.name,
                                  bom_line_id.product_id.name_get()[0][1]))
            quantity = self._factor(
                bom_line_id.product_qty * factor,
                bom_line_id.product_efficiency, bom_line_id.product_rounding)
            bom_id = self._bom_find_prepare(bom_line_id, properties=properties)
            # If BoM should not behave like PhantoM, just add the product,
            # otherwise explode further
            if (bom_line_id.type != "phantom" and
                    (not bom_id or self.browse(bom_id).type != "phantom")):
                result.append(
                    self._prepare_consume_line(bom_line_id, quantity, factor))
            elif bom_id:
                all_prod = [bom.product_tmpl_id.id] + (previous_products or [])
                bom2 = self.browse(bom_id)
                # We need to convert to units/UoM of chosen BoM
                factor2 = uom_obj._compute_qty(
                    bom_line_id.product_uom.id, quantity, bom2.product_uom.id)
                quantity2 = factor2 / bom2.product_qty
                res = bom2._bom_explode(
                    bom_line_id.product_id, quantity2, properties=properties,
                    level=level + 10, previous_products=all_prod,
                    master_bom=master_bom)
                result = result + res[0]
                result2 = result2 + res[1]
            else:
                raise UserError(
                    _('BoM "%s" contains a phantom BoM line but the product '
                      '"%s" does not have any BoM defined.') %
                    (master_bom.name, self._get_bom_product_name(bom_line_id)))
        return result, result2
