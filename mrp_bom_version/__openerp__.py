# -*- coding: utf-8 -*-
# (c) 2015 Alfredo de la Fuente - AvanzOSC
# (c) 2015 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "MRP - BoM version",
    "summary": "BoM versioning",
    "version": "8.0.1.0.0",
    "license": "AGPL-3",
    "author": "OdooMRP team,"
              "AvanzOSC,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza, "
              "Odoo Community Association (OCA)",
    "website": "http://www.odoomrp.com",
    "contributors": [
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
        "Ana Juaristi <anajuaristi@avanzosc.es>",
        "Alfredo de la Fuente <alfredodelafuente@avanzosc.es>",
        "Oihane Crucelaegui <oihanecrucelaegui@avanzosc.es>",
    ],
    "category": "Manufacturing",
    "depends": [
        "mrp",
    ],
    "data": [
        "data/mrp_bom_data.xml",
        "security/mrp_bom_version_security.xml",
        "views/res_config_view.xml",
        "views/mrp_bom_view.xml",
    ],
    "installable": True,
    "post_init_hook": "set_active_bom_active_state",
}
