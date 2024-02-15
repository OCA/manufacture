from odoo.tools import config

from . import (
    input_config,
    input_constraint,
    input_line,
    input_line_wizard,
    mrp_bom,
    mrp_bom_configured,
    mrp_bom_line,
)

if not config["without_demo"] or config["test_enable"]:
    from . import demo_input_mixin
