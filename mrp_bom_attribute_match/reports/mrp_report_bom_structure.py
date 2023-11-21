from odoo import Command, models
from odoo.tools import float_compare, float_round, format_date, float_is_zero


class ReportBomStructure(models.AbstractModel):
    _inherit = "report.mrp.report_bom_structure"

    def _has_attachments(self, data):
        if data:
            return data['attachment_ids'] or any(self._has_attachments(component) for component in data.get('components', []))
        else:
            return False

    def _get_report_data(self, bom_id, searchQty=0, searchVariant=False):
        lines = {}
        bom = self.env['mrp.bom'].browse(bom_id)
        bom_quantity = searchQty or bom.product_qty or 1
        bom_product_variants = {}
        bom_uom_name = ''

        if searchVariant:
            product = self.env['product.product'].browse(int(searchVariant))
        else:
            product = bom.product_id or bom.product_tmpl_id.product_variant_id

        if bom:
            bom_uom_name = bom.product_uom_id.name

            # Get variants used for search
            if not bom.product_id:
                for variant in bom.product_tmpl_id.product_variant_ids:
                    bom_product_variants[variant.id] = variant.display_name

        if self.env.context.get('warehouse'):
            warehouse = self.env['stock.warehouse'].browse(self.env.context.get('warehouse'))
        else:
            warehouse = self.env['stock.warehouse'].browse(self.get_warehouses()[0]['id'])

        lines = self._get_bom_data(bom, warehouse, product=product, line_qty=bom_quantity, level=0)
        if lines:
            production_capacities = self._compute_production_capacities(bom_quantity, lines)
            lines.update(production_capacities)
        return {
            'lines': lines,
            'variants': bom_product_variants,
            'bom_uom_name': bom_uom_name,
            'bom_qty': bom_quantity,
            'is_variant_applied': self.env.user.user_has_groups('product.group_product_variant') and len(
                bom_product_variants) > 1,
            'is_uom_applied': self.env.user.user_has_groups('uom.group_uom'),
            'precision': self.env['decimal.precision'].precision_get('Product Unit of Measure'),
        }

    def _get_bom_data(self, bom, warehouse, product=False, line_qty=False, bom_line=False, level=0, parent_bom=False,
                      parent_product=False, index=0, product_info=False, ignore_stock=False):
        """ Gets recursively the BoM and all its subassemblies and computes availibility estimations for each component and their disponibility in stock.
            Accepts specific keys in context that will affect the data computed :
            - 'minimized': Will cut all data not required to compute availability estimations.
            - 'from_date': Gives a single value for 'today' across the functions, as well as using this date in products quantity computes.
        """
        is_minimized = self.env.context.get('minimized', False)
        if not product:
            product = bom.product_id or bom.product_tmpl_id.product_variant_id
        if not line_qty:
            line_qty = bom.product_qty

        if not product_info:
            product_info = {}
        key = product.id
        if key not in product_info:
            product_info[key] = {'consumptions': {'in_stock': 0}}

        company = bom.company_id or self.env.company
        current_quantity = line_qty
        if bom_line:
            current_quantity = bom_line.product_uom_id._compute_quantity(line_qty, bom.product_uom_id) or 0

        prod_cost = 0
        attachment_ids = []
        if not is_minimized:
            if product:
                prod_cost = product.uom_id._compute_price(product.with_company(company).standard_price,
                                                          bom.product_uom_id) * current_quantity
                attachment_ids = self.env['mrp.document'].search(['|', '&', ('res_model', '=', 'product.product'),
                                                                  ('res_id', '=', product.id), '&',
                                                                  ('res_model', '=', 'product.template'),
                                                                  ('res_id', '=', product.product_tmpl_id.id)]).ids
            else:
                # Use the product template instead of the variant
                prod_cost = bom.product_tmpl_id.uom_id._compute_price(
                    bom.product_tmpl_id.with_company(company).standard_price, bom.product_uom_id) * current_quantity
                attachment_ids = self.env['mrp.document'].search(
                    [('res_model', '=', 'product.template'), ('res_id', '=', bom.product_tmpl_id.id)]).ids

        bom_key = bom.id
        if not product_info[key].get(bom_key):
            product_info[key][bom_key] = self._get_resupply_route_info(warehouse, product, current_quantity,
                                                                       product_info, bom, parent_bom, parent_product)
        route_info = product_info[key].get(bom_key, {})
        quantities_info = {}
        if not ignore_stock:
            # Useless to compute quantities_info if it's not going to be used later on
            quantities_info = self._get_quantities_info(product, bom.product_uom_id, product_info, parent_bom,
                                                        parent_product)

        bom_report_line = {
            'index': index,
            'bom': bom,
            'bom_id': bom and bom.id or False,
            'bom_code': bom and bom.code or False,
            'type': 'bom',
            'quantity': current_quantity,
            'quantity_available': quantities_info.get('free_qty', 0),
            'quantity_on_hand': quantities_info.get('on_hand_qty', 0),
            'base_bom_line_qty': bom_line.product_qty if bom_line else False,
            # bom_line isn't defined only for the top-level product
            'name': product.display_name or bom.product_tmpl_id.display_name,
            'uom': bom.product_uom_id if bom else product.uom_id,
            'uom_name': bom.product_uom_id.name if bom else product.uom_id.name,
            'route_type': route_info.get('route_type', ''),
            'route_name': route_info.get('route_name', ''),
            'route_detail': route_info.get('route_detail', ''),
            'lead_time': route_info.get('lead_time', False),
            'currency': company.currency_id,
            'currency_id': company.currency_id.id,
            'product': product,
            'product_id': product.id,
            'link_id': (
                           product.id if product.product_variant_count > 1 else product.product_tmpl_id.id) or bom.product_tmpl_id.id,
            'link_model': 'product.product' if product.product_variant_count > 1 else 'product.template',
            'code': bom and bom.display_name or '',
            'prod_cost': prod_cost,
            'bom_cost': 0,
            'level': level or 0,
            'attachment_ids': attachment_ids,
            'phantom_bom': bom.type == 'phantom',
            'parent_id': parent_bom and parent_bom.id or False,
        }

        if not is_minimized:
            operations = self._get_operation_line(product, bom, float_round(current_quantity, precision_rounding=1,
                                                                            rounding_method='UP'), level + 1, index)
            bom_report_line['operations'] = operations
            bom_report_line['operations_cost'] = sum([op['bom_cost'] for op in operations])
            bom_report_line['operations_time'] = sum([op['quantity'] for op in operations])
            bom_report_line['bom_cost'] += bom_report_line['operations_cost']

        components = []
        for component_index, line in enumerate(bom.bom_line_ids):
            new_index = f"{index}{component_index}"
            if product and line._skip_bom_line(product):
                continue
            line_quantity = (current_quantity / (bom.product_qty or 1.0)) * line.product_qty
            if line.child_bom_id:
                component = self._get_bom_data(line.child_bom_id, warehouse, line.product_id, line_quantity,
                                               bom_line=line, level=level + 1, parent_bom=bom,
                                               parent_product=product, index=new_index, product_info=product_info,
                                               ignore_stock=ignore_stock)
            else:
                component = self._get_component_data(bom, product, warehouse, line, line_quantity, level + 1, new_index,
                                                     product_info, ignore_stock)

            for component_bom in components:
                if component['product_id'] == component_bom['product_id'] and component['uom'].id == component_bom[
                    'uom'].id:
                    self._merge_components(component_bom, component)
                    break
            else:
                if not component:
                    return []
                components.append(component)
            bom_report_line['bom_cost'] += component['bom_cost']
        bom_report_line['components'] = components
        bom_report_line['producible_qty'] = self._compute_current_production_capacity(bom_report_line)

        if not is_minimized:
            byproducts, byproduct_cost_portion = self._get_byproducts_lines(product, bom, current_quantity, level + 1,
                                                                            bom_report_line['bom_cost'], index)
            bom_report_line['byproducts'] = byproducts
            bom_report_line['cost_share'] = float_round(1 - byproduct_cost_portion, precision_rounding=0.0001)
            bom_report_line['byproducts_cost'] = sum(byproduct['bom_cost'] for byproduct in byproducts)
            bom_report_line['byproducts_total'] = sum(byproduct['quantity'] for byproduct in byproducts)
            bom_report_line['bom_cost'] *= bom_report_line['cost_share']

        availabilities = self._get_availabilities(product, current_quantity, product_info, bom_key, quantities_info,
                                                  level, ignore_stock, components, bom_report_line)
        bom_report_line.update(availabilities)

        if level == 0:
            # Gives a unique key for the first line that indicates if product is ready for production right now.
            bom_report_line['components_available'] = all([c['stock_avail_state'] == 'available' for c in components])
        return bom_report_line

    def _get_component_data(self, parent_bom, parent_product, warehouse, bom_line, line_quantity, level, index, product_info, ignore_stock):
        line = bom_line
        if line.component_template_id:
            bom = bom_line.bom_id
            bom = bom.new(origin=bom)
            product = parent_product
            to_ignore_line_ids = []
            if line._skip_bom_line(product) or not line.component_template_id:
                return []
            line_product = bom._get_component_template_product(
                line, product, line.product_id
            )
            if not line_product:
                to_ignore_line_ids.append(line.id)
                return []
            else:
                line.product_id = line_product
            if to_ignore_line_ids:
                bom.bom_line_ids = [Command.unlink(id) for id in to_ignore_line_ids]
        component = super()._get_component_data(
            parent_bom, parent_product, warehouse, bom_line, line_quantity, level, index, product_info, ignore_stock
        )
        if line.component_template_id:
            line.product_id = False
        return component
