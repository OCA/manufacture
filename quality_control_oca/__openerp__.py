# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 NaN Projectes de Programari Lliure, S.L.
#                    All Rights Reserved.
#                    http://www.NaN-tic.com
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

{
    "name": "Quality Control",
    "version": "0.1",
    "author": "NaN·tic",
    "contributors": [
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
    ],
    "category": "Generic Modules/Others",
    "summary": "Quality control",
    "description": """
This module provides a generic infrastructure for quality tests. The idea is
that it can be later be reused for doing quality tests in production lots but
also in any other areas a company may desire.

Developed for Trod y Avia, S.L.""",
    "depends": [
        'product'
    ],
    "data": [
        'data/quality_control_data.xml',
        'security/quality_control_security.xml',
        'security/ir.model.access.csv',
        'workflow/test_workflow.xml',
        'wizard/qc_test_wizard_view.xml',
        'views/quality_control_view.xml',
    ],
    "installable": True,
}
