from collections import defaultdict
from itertools import groupby

from dateutil.relativedelta import relativedelta

from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.tools import float_compare

from odoo.addons.stock.models.stock_rule import ProcurementException


class StockPicking(models.Model):
    _inherit = "stock.rule"

    @api.model
    def _run_buy(self, procurements):
        """Launching a purchase group with required/custom
        fields generated by a sales order line"""
        procurements_by_po_domain = defaultdict(list)
        errors = []
        message = _(
            """There is no matching vendor price to generate the purchase order for
                product %s (no vendor defined,  minimum quantity not reached,
                dates not valid, ...).
                Go on the product form and complete the list of vendors."""
        )
        for procurement, rule in procurements:
            supplier = self._get_supplier(procurement)
            if not supplier:
                errors.append(
                    (procurement, message % (procurement.product_id.display_name))
                )
            partner = supplier.name
            # we put `supplier_info` in values for extensibility purposes
            procurement.values.update(
                {"supplier": supplier, "propagate_cancel": rule.propagate_cancel}
            )
            domain = rule._make_po_get_domain(
                procurement.company_id, procurement.values, partner
            )
            procurements_by_po_domain[domain].append((procurement, rule))
        if errors:
            raise ProcurementException(errors)
        self._create_po_not_exist(procurements_by_po_domain)

    def _prepare_purchase_order(self, company_id, origins, values):
        """Returns prepared data for create PO"""
        if (
            "partner_id" not in values[0]
            and company_id.subcontracting_location_id.parent_path
            in self.location_id.parent_path
        ):
            values[0]["partner_id"] = values[0]["group_id"].partner_id.id
        return super()._prepare_purchase_order(company_id, origins, values)

    @api.model
    def _get_supplier(self, procurement):
        """Return valid supplier"""
        supplier = False
        # Get the schedule date in order to find a valid seller
        procurement_date_planned = fields.Datetime.from_string(
            procurement.values["date_planned"]
        )
        if procurement.values.get("supplierinfo_id"):
            supplier = procurement.values["supplierinfo_id"]
        elif (
            procurement.values.get("orderpoint_id")
            and procurement.values["orderpoint_id"].supplier_id
        ):
            supplier = procurement.values["orderpoint_id"].supplier_id
        else:
            supplier = procurement.product_id.with_company(
                procurement.company_id.id
            )._select_seller(
                partner_id=procurement.values.get("supplierinfo_name"),
                quantity=procurement.product_qty,
                date=procurement_date_planned.date(),
                uom_id=procurement.product_uom,
            )
        # Fall back on a supplier for which no price may be defined.
        # Not ideal, but better than blocking the user.
        supplier = (
            supplier
            or procurement.product_id._prepare_sellers(False).filtered(
                lambda s: not s.company_id or s.company_id == procurement.company_id
            )[:1]
        )
        return supplier

    @api.model
    def _create_po_not_exist(self, procurements_by_po_domain):
        pol_obj = self.env["purchase.order.line"]
        for domain, procurements_rules in procurements_by_po_domain.items():
            # Get the procurements for the current domain.
            # Get the rules for the current domain. Their only use is to create
            # the PO if it does not exist.
            procurements, rules = zip(*procurements_rules)
            # Check if a PO exists for the current domain.
            company_id = procurements[0].company_id
            po = self._check_po_exists(domain, procurements, rules, company_id)
            procurements_to_merge = self._get_procurements_to_merge(procurements)
            procurements = self._merge_procurements(procurements_to_merge)
            po_lines_by_product = {}
            grouped_po_lines = groupby(
                po.order_line.filtered(
                    lambda l: not l.display_type
                    and l.product_uom == l.product_id.uom_po_id
                ).sorted(lambda l: l.product_id.id),
                key=lambda l: l.product_id.id,
            )
            for product, po_lines in grouped_po_lines:
                po_lines_by_product[product] = pol_obj.concat(*list(po_lines))
            po_line_values = []
            for procurement in procurements:
                po_lines = po_lines_by_product.get(procurement.product_id.id, pol_obj)
                po_line = po_lines._find_candidate(*procurement)

                if po_line:
                    # If the procurement can be merge in an existing line. Directly
                    # write the new values on it.
                    vals = self._update_purchase_order_line(
                        procurement.product_id,
                        procurement.product_qty,
                        procurement.product_uom,
                        company_id,
                        procurement.values,
                        po_line,
                    )
                    po_line.write(vals)
                else:
                    if (
                        float_compare(
                            procurement.product_qty,
                            0,
                            precision_rounding=procurement.product_uom.rounding,
                        )
                        <= 0
                    ):
                        # If procurement contains negative quantity,
                        # don't create a new line that would contain negative qty
                        continue
                    # If it does not exist a PO line for current procurement.
                    # Generate the create values for it and add it to a list in
                    # order to create it in batch.
                    po_line_values.append(
                        pol_obj._prepare_purchase_order_line_from_procurement(
                            procurement.product_id,
                            procurement.product_qty,
                            procurement.product_uom,
                            procurement.company_id,
                            procurement.values,
                            po,
                        )
                    )
                    # Check if we need to advance the order date for the new line
                    date_planned = procurement.values["date_planned"]
                    order_date_planned = date_planned - relativedelta(
                        days=procurement.values["supplier"].delay
                    )
                    if fields.Date.to_date(order_date_planned) < fields.Date.to_date(
                        po.date_order
                    ):
                        po.date_order = order_date_planned
            pol_obj.sudo().create(po_line_values)

    @api.model
    def _check_po_exists(self, domain, procurements, rules, company_id):
        """Check if a PO exists for the current domain"""
        po_obj = self.env["purchase.order"]
        origins = {p.origin for p in procurements}
        po = po_obj.sudo().search([dom for dom in domain], limit=1)
        # Get the set of procurement origin for the current domain.
        if not po:
            positive_values = [
                p.values
                for p in procurements
                if float_compare(
                    p.product_qty, 0.0, precision_rounding=p.product_uom.rounding
                )
                >= 0
            ]
            if positive_values:
                # We need a rule to generate the PO. However the rule generated
                # the same domain for PO and the _prepare_purchase_order method
                # should only uses the common rules's fields.
                vals = rules[0]._prepare_purchase_order(
                    company_id, origins, positive_values
                )
                # The company_id is the same for all procurements since
                # _make_po_get_domain add the company in the domain.
                # We use SUPERUSER_ID since
                # we don't want the current user to be follower of the PO.
                # Indeed, the current user may be a user without access to Purchase,
                # or even be a portal user.
                po = (
                    po_obj.with_company(company_id).with_user(SUPERUSER_ID).create(vals)
                )

        else:
            # If a purchase order is found, adapt its `origin` field.
            if po.origin:
                missing_origins = origins - set(po.origin.split(", "))
                if missing_origins:
                    po.write(
                        {
                            "origin": "{} {}".format(
                                po.origin, ", ".join(missing_origins)
                            )
                        }
                    )
            else:
                new_origin = ", ".join(origins)
                po.write({"origin": f"{new_origin}"})
        return po
