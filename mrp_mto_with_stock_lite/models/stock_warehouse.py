# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    pbm_mts_mto_rule_id = fields.Many2one(
        'stock.rule',
        'Picking Before Manufacturing MTO+MTS Rule',
    )

    @api.constrains('mto_mts_management', 'manufacture_to_resupply',
                    'manufacture_steps')
    def _check_mrp_mto_with_stock(self):
        bad_settings = self.search([
            ('mto_mts_management', '=', True),
            ('manufacture_to_resupply', '=', True),
            ('manufacture_steps', '=', 'mrp_one_step'),
        ], limit=1)
        if bad_settings:
            raise ValidationError(_(
                "Not allowed use MTO+MTS rules with Manufacture (1 step)!"))

    def _get_all_routes(self):
        routes = super(StockWarehouse, self)._get_all_routes()
        routes |= self.mapped('pbm_mts_mto_rule_id.route_id')
        return routes

    def _update_name_and_code(self, new_name=False, new_code=False):
        res = super(StockWarehouse, self)._update_name_and_code(new_name,
                                                                new_code)
        if not new_name:
            return res
        for wh in self.filtered('pbm_mts_mto_rule_id'):
            rule = wh.pbm_mts_mto_rule_id
            rule.write({
                'name': rule.name.replace(wh.name, new_name, 1),
            })
        return res

    def _get_global_route_rules_values(self):
        rule = self.get_rules_dict()[self.id]['pbm']
        rule = [
            r for r in rule
            if (r.from_loc == self.lot_stock_id
                and r.dest_loc == self.pbm_loc_id
                and r.picking_type == self.pbm_type_id)
        ][0]
        location = rule.from_loc
        location_dest = rule.dest_loc
        picking_type = rule.picking_type
        rules = super()._get_global_route_rules_values()
        can_use_mts_mto = (self.mto_mts_management
                           and self.manufacture_to_resupply
                           and self.manufacture_steps != 'mrp_one_step')
        rules.update({
            'pbm_mts_mto_rule_id': {
                'depends': ['mto_mts_management',
                            'manufacture_to_resupply',
                            'manufacture_steps'],
                'create_values': {
                    'action': 'pull',
                    'procure_method': 'make_to_order',
                    'company_id': self.company_id.id,
                    'auto': 'manual',
                    'propagate': True,
                    'route_id': self._find_global_route(
                        'stock_mts_mto_rule.route_mto_mts',
                        _('Make To Order + Make To Stock')).id,
                    'sequence': 10,
                },
                'update_values': {
                    'active': can_use_mts_mto,
                    'name': self._format_rulename(location,
                                                  location_dest,
                                                  'MTS+MTO'),
                    'location_id': location_dest.id,
                    'location_src_id': location.id,
                    'picking_type_id': picking_type.id,
                }
            },
        })
        return rules

    def _create_or_update_global_routes_rules(self):
        res = super()._create_or_update_global_routes_rules()
        need_init_pbm_mts_mto_rule = (
            self.mto_mts_management
            and self.manufacture_to_resupply
            and self.manufacture_steps != 'mrp_one_step'
            and self.pbm_mts_mto_rule_id
            and self.pbm_mts_mto_rule_id.action != 'split_procurement'
        )
        if need_init_pbm_mts_mto_rule:
            # Cannot create or update with the 'split_procurement' action due
            # to constraint and the fact that the constrained rule_ids may
            # not exist during the initial (or really any) calls of
            # _get_global_route_rules_values
            pbm_mts_mto_rule = self.pbm_mts_mto_rule_id
            rule = self.env['stock.rule'].search([
                ('location_id', '=', pbm_mts_mto_rule.location_id.id),
                ('location_src_id', '=', pbm_mts_mto_rule.location_src_id.id),
                ('route_id', '=', self.pbm_route_id.id),
                ('id', '!=', pbm_mts_mto_rule.id),
            ], limit=1)
            if rule:
                pbm_mts_mto_rule.write({
                    'action': 'split_procurement',
                    'mts_rule_id': rule.id,
                    'mto_rule_id': self.pbm_mto_pull_id.id,
                })
        return res
