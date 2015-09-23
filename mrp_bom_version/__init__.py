# -*- coding: utf-8 -*-
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from . import models


def set_active_bom_active_state(cr, registry):
    """Set those active BoMs to state 'active'"""
    cr.execute("""UPDATE mrp_bom
                     SET state = 'active'
                   WHERE active = True""")
