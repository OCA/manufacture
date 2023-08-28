from odoo import models


class ReportBomConfigurable(models.AbstractModel):
    _inherit = "report.mrp.report_bom_structure"
    _name = "report.mrp_bom_configurable.bom_configurable"
    _description = "Configurable BOM Report"

    def _get_report_values(self, docids, data):
        model = self.env["report.mrp.report_bom_structure"]
        res = model.with_context(variable=1)._get_report_values(docids, data)
        return res


# TODO
# see https://github.com/OCA/manufacture-reporting/pull/113/files for xlsx output
# OR
# https://github.com/OCA/spreadsheet
