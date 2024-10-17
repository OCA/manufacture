# Copyright 2024 Akretion France (https://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import get_lang


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    bom_id = fields.Many2one(
        "mrp.bom",
        string="Subcontracting Bill of Material",
        check_company=True,
        domain="""[
        '&',
            '|',
                ('company_id', '=', False),
                ('company_id', '=', company_id),
            '&',
                '|',
                    ('product_id', '=', product_id),
                    '&',
                        ('product_tmpl_id.product_variant_ids', '=', product_id),
                        ('product_id', '=', False),
                ('type', '=', 'subcontract')]
        """,
    )

    @api.constrains("product_id", "bom_id", "display_type")
    def _check_bom_id(self):
        for line in self:
            bom = line.bom_id
            if bom:
                if bom.type != "subcontract":
                    raise ValidationError(
                        _(
                            "On purchase order line '%(po_line)s', the selected "
                            "bill of material '%(bom)s' is not a subcontract "
                            "bill of material.",
                            po_line=line.display_name,
                            bom=bom.display_name,
                        )
                    )
                if line.display_type:
                    raise ValidationError(
                        _(
                            "You cannot select a subcontracting bill of material "
                            "on purchase order line '%s' which is a section or note line."
                        )
                        % line.display_name
                    )
                if not line.product_id:
                    raise ValidationError(
                        _(
                            "You cannot select a subcontracting bill of material "
                            "on purchase order line '%s' which doesn't have a product."
                        )
                        % line.display_name
                    )
                if bom.product_id:
                    if line.product_id != bom.product_id:
                        raise ValidationError(
                            _(
                                "On purchase order line '%(po_line)s', the selected "
                                "bill of material '%(bom)s' doesn't apply on "
                                "product '%(product)s.'",
                                po_line=line.display_name,
                                bom=bom.display_name,
                                product=line.product_id.display_name,
                            )
                        )
                else:  # product_tmpl_id is a required field on mrp.bom
                    if line.product_id not in bom.product_tmpl_id.product_variant_ids:
                        raise ValidationError(
                            _(
                                "On purchase order line '%(po_line)s', the selected "
                                "bill of material '%(bom)s' doesn't apply on "
                                "product '%(product)s.'",
                                po_line=line.display_name,
                                bom=bom.display_name,
                                product=line.product_id.display_name,
                            )
                        )
                order = line.order_id
                if bom.picking_type_id and bom.picking_type_id != order.picking_type_id:
                    raise ValidationError(
                        _(
                            "On purchase order line '%(po_line)s', the selected "
                            "bill of material '%(bom)s' is configured for "
                            "operation '%(bom_picking_type)s' but the purchase order "
                            "%(po)s is configured to deliver to '%(po_picking_type)s'.",
                            po_line=line.display_name,
                            bom=bom.display_name,
                            bom_picking_type=bom.picking_type_id.display_name,
                            po=order.name,
                            po_picking_type=order.picking_type_id.display_name,
                        )
                    )
                if (
                    bom.subcontractor_ids
                    and order.partner_id.commercial_partner_id
                    not in bom.subcontractor_ids.commercial_partner_id
                ):
                    raise ValidationError(
                        _(
                            "On purchase order line '%(po_line)s', the selected "
                            "bill of material '%(bom)s' is linked to subcontractors "
                            "'%(subcontractors)s', but the purchase order "
                            "%(po)s is linked to supplier %(supplier)s.",
                            po_line=line.display_name,
                            bom=bom.display_name,
                            subcontractors=", ".join(
                                [p.display_name for p in bom.subcontractor_ids]
                            ),
                            po=order.name,
                            supplier=order.partner_id.display_name,
                        )
                    )

    def _get_product_purchase_description(self, product_lang):
        name = super()._get_product_purchase_description(product_lang)
        if self.bom_id and name:
            bom = self.bom_id.with_context(
                lang=get_lang(self.env, self.partner_id.lang).code
            )
            if bom.subcontract_purchase_description:
                name = "\n".join([name, bom.subcontract_purchase_description])
        return name

    @api.onchange("bom_id")
    def bom_id_change(self):
        if self.product_id:
            product_lang = self.product_id.with_context(
                lang=get_lang(self.env, self.partner_id.lang).code,
                partner_id=self.partner_id.id,
                company_id=self.company_id.id,
            )
            self.name = self._get_product_purchase_description(product_lang)

    def _product_id_change(self):
        res = super()._product_id_change()
        # reset bom when product changes
        self.bom_id = False
        return res
