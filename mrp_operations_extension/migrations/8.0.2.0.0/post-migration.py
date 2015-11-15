# -*- coding: utf-8 -*-
# (c) 2015 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp.addons.mrp_operations_extension import (
    create_default_routing_workcenter_line)


def migrate(cr, version):
    create_default_routing_workcenter_line(cr)
