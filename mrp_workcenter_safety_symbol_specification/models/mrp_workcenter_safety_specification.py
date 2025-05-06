from odoo import fields, models


class MrpWorkcenterSafetySpecification(models.Model):
    """Intermediate model to link Symbols with Specifications on Work Centers."""

    _name = "mrp.workcenter.safety.specification"
    _description = "Work Center Safety Symbol Specification"
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    workcenter_id = fields.Many2one(
        "mrp.workcenter",
        string="Work Center",
        required=True,
        ondelete="cascade",
        index=True,
    )

    # === RENAMED FIELD ===
    iso_symbol_id = fields.Many2one(
        "iso7010.symbol",
        string="Safety Symbol",
        required=True,
        ondelete="cascade",
        domain="[('active', '=', True)]",
    )  # Only allow selecting active symbols
    # === END OF RENAMED FIELD ===

    specification_notes = fields.Text(
        string="Specification / Notes",
        help="Add specific details, e.g., 'Type P2 required', "
        "'Use chemical resistant variant', 'Check before each use'.",
    )
    # === UPDATED RELATED FIELDS ===
    symbol_image = fields.Image(related="iso_symbol_id.image", readonly=True)
    symbol_code = fields.Char(related="iso_symbol_id.iso_code", readonly=True)
    # === END OF UPDATED RELATED FIELDS ===

    _sql_constraints = [
        # === UPDATED SQL CONSTRAINT ===
        (
            "workcenter_symbol_uniq",
            "unique(workcenter_id, iso_symbol_id)",
            "Each symbol can only be linked once per work center in specifications.",
        )
        # === END OF UPDATED SQL CONSTRAINT ===
    ]
