# Copyright 2025 Edilio Escalona Almira - Binhexteam
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class QcTest(models.Model):
    _inherit = "qc.test"

    enable_image = fields.Boolean(
        help="""
        Allows the possibility of attaching an image
        to the questions defined in the inspection.
        """
    )
    is_required_image = fields.Boolean(
        string="Required image",
        default=False,
        help="""
            Allows the obligation to attach an image in
            the questions defined in the inspection.
        """,
    )
