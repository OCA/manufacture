from . import input_config
from . import input_line
from . import input_constraint
from . import mrp_bom
from . import mrp_bom_line

from odoo.tools import config

if not config["without_demo"] or config["test_enable"]:
    from . import demo_input_mixin
