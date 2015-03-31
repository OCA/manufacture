# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from . import models
from . import wizards
from openerp import SUPERUSER_ID


def set_bill_of_material_references(cr, registry):
    """
    This function adds a reference record to each existing boms when the
    module is installed. This ensures that each bom has a reference
    so that the module works properly.
    """
    bom_obj = registry['mrp.bom']
    ref_obj = registry['mrp.bom.reference']
    bom_ids = bom_obj.search(cr, SUPERUSER_ID, [])
    for bom in bom_obj.browse(cr, SUPERUSER_ID, bom_ids):
        if not bom.reference_id:
            ref_obj.create(cr, SUPERUSER_ID, {'bom_id': bom.id})
