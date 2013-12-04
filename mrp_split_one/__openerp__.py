# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#   Author: Leonardo Pistone <leonardo.pistone@camptocamp.com>                #
#   Copyright 2013 Camptocamp SA                                              #
#                                                                             #
#   This program is free software: you can redistribute it and/or modify      #
#   it under the terms of the GNU Affero General Public License as            #
#   published by the Free Software Foundation, either version 3 of the        #
#   License, or (at your option) any later version.                           #
#                                                                             #
#   This program is distributed in the hope that it will be useful,           #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#   GNU Affero General Public License for more details.                       #
#                                                                             #
#   You should have received a copy of the GNU Affero General Public License  #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                             #
###############################################################################

{'name': 'MRP Split One',
 'version': '0.1',
 'category': 'Generic Modules/Others',
 'license': 'AGPL-3',
 'description': """MRP Split one unit in a production order.

This module adds a button in each line of the Products to Finish and Finished
Products to directly split one unit of the product in a separate line.
After the split the page needs to be reloaded because of the bug lp:1083253.
""",
 'complexity': 'easy',
 'author': 'Camptocamp',
 'website': 'http://www.camptocamp.com/',
 'depends': ['mrp'],
 'init_xml': [],
 'update_xml': ['mrp_view.xml'],
 'demo_xml': [],
 'installable': True,
 'active': False,
 }
