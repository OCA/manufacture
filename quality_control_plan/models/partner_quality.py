# Copyright 2010 NaN Projectes de Programari Lliure, S.L.
# Copyright 2014 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2014 Oihane Crucelaegui - AvanzOSC
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Simone Rubino - Agile Business Group
# Copyright 2019 Marcelo Frare (Ass. PNLUG - Gruppo Odoo <http://odoo.pnlug.it>)
# Copyright 2019 Stefano Consolaro (Ass. PNLUG - Gruppo Odoo <http://odoo.pnlug.it>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MgmtsystemMgmPartner(models.Model):
    """
    Extend res.partner with contact info for communications on quality
    and quality control triggers
    """

    # extended model
    _inherit = ['res.partner']

    # new fields
    # name of the person to contact
    quality_contact_name = fields.Char('Contact Name')
    # e-mail of contact
    quality_contact_email = fields.Char('Email')
    # trigger to activate inspection
    qc_triggers = fields.One2many(
        comodel_name="qc.trigger.partner_line",
        inverse_name="partner",
        string="Quality control triggers"
        )
