# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import base64

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class QcInspection(models.Model):
    _inherit = "qc.inspection"

    sign_request_ids = fields.One2many(
        "sign.oca.request", "inspection_id", string="Sign Requests"
    )

    sign_request_count = fields.Integer(compute="_compute_sign_request_count")

    signed = fields.Boolean(compute="_compute_signed")

    current_sign_request_id = fields.Many2one(
        "sign.oca.request",
        compute="_compute_current_sign_request",
        store=False,
    )

    def _compute_sign_request_count(self):
        for rec in self:
            rec.sign_request_count = len(rec.sign_request_ids)

    @api.depends("sign_request_ids.state")
    def _compute_signed(self):
        for rec in self:
            rec.signed = any(req.state == "2_signed" for req in rec.sign_request_ids)

    def _compute_current_sign_request(self):
        for rec in self:
            rec.current_sign_request_id = rec.sign_request_ids[:1]

    def _get_signature_positions_by_role(self, report):
        self.ensure_one()

        positions = self.env["qc.sign.template.item"].search(
            [
                ("report_id", "=", report.id),
                ("company_id", "=", self.company_id.id),
            ]
        )
        if not positions:
            raise UserError(
                _(
                    "No signature position configuration found for report '%s'.",
                    report.name,
                )
            )

        grouped = {}
        for pos in positions:
            role = pos.role_id
            if not role:
                raise ValidationError(
                    _(
                        "Signature position on report '%(report)s' "
                        "(page %(page)s) has no role.",
                        report=report.name,
                        page=pos.page,
                    )
                )
            grouped.setdefault(role, self.env["qc.sign.template.item"])
            grouped[role] |= pos
        return grouped

    def _generate_template_from_report(self, report):
        self.ensure_one()
        pdf_content, _ = report._render_qweb_pdf(report.report_name, res_ids=self.ids)
        if not pdf_content:
            raise UserError(_("Could not generate PDF for picking %s.", self.name))

        filename = f"{report.name} - {self.name}.pdf"

        signature_field = self.env["sign.oca.field"].search(
            [("field_type", "=", "signature")], limit=1
        )
        if not signature_field:
            raise ValidationError(
                _(
                    "No signature field configured in sign_oca "
                    "(field_type='signature')."
                )
            )

        inspection_model = self.env["ir.model"]._get("qc.inspection")

        template = self.env["sign.oca.template"].create(
            {
                "name": filename,
                "data": base64.b64encode(pdf_content),
                "filename": filename,
                "model_id": inspection_model.id if inspection_model else False,
            }
        )

        positions_by_role = self._get_signature_positions_by_role(report)

        for role, positions in positions_by_role.items():
            for pos in positions:
                self.env["sign.oca.template.item"].create(
                    {
                        "template_id": template.id,
                        "field_id": signature_field.id,
                        "role_id": role.id,
                        "page": pos.page,
                        "position_x": pos.position_x,
                        "position_y": pos.position_y,
                        "width": pos.width,
                        "height": pos.height,
                        "required": True,
                    }
                )

        return template, positions_by_role

    def _get_sign_report(self):
        self.ensure_one()

        report_id = self.env["ir.config_parameter"].get_param(
            "quality_control_sign_oca.quality_inspection_report_id"
        )

        if not report_id:
            raise UserError(
                _("No Inspection Report configured for signature in Settings.")
            )

        report = self.env["ir.actions.report"].browse(int(report_id))

        if not report or not report.exists():
            raise UserError(
                _("Configured inspection report not found or has been deleted.")
            )

        return report

    def action_view_sign_requests(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Sign Requests",
            "res_model": "sign.oca.request",
            "view_mode": "list,form",
            "domain": [("inspection_id", "=", self.id)],
        }

    def action_sign_inspection(self):
        self.ensure_one()

        report = self._get_sign_report()
        template, slots_by_role = self._generate_template_from_report(report)

        request_items = []
        for role, _positions in slots_by_role.items():
            partner = self.env.user.partner_id
            if partner:
                request_items.append(
                    (
                        0,
                        0,
                        {
                            "role_id": role.id,
                            "partner_id": partner.id,
                        },
                    )
                )

        if not request_items:
            raise UserError(_("No signers found for this inspection."))

        req = self.env["sign.oca.request"].create(
            {
                "name": f"Inspection {self.name}",
                "template_id": template.id,
                "signatory_data": template._get_signatory_data(),
                "record_ref": f"{self._name},{self.id}",  # noqa: E231
                "data": template.data,
                "ask_location": template.ask_location,
                "inspection_id": self.id,
                "signer_ids": request_items,
            }
        )

        req.action_send(sign_now=True)

        return req.sign()
