from odoo import api, models
from odoo import fields, models, api

class ReportBomStructure(models.AbstractModel):
    _name = 'mrp_bom_variable.report.mrp.report_bom_structure'
    _inherit = 'report.mrp.report_bom_structure'

    @api.model
    def _get_bom_data(self, *args, **kwargs):
        bom_report_line = super(ReportBomStructure, self)._get_bom_data(*args, **kwargs)
        bom_line = kwargs.get('bom_line', False)

        bom_report_line['domain'] = bom_line.domain if bom_line else False

        return bom_report_line

    # @api.model
    # def _get_operation_line(self, *args, **kwargs):
    #     operations = super(ReportBomStructure, self)._get_operation_line(*args, **kwargs)
    #     bom = args[1]

    #     index = 0
    #     for operation in bom.operation_ids:
    #         if not product or operation._skip_operation_line(product):
    #             continue
    #         operations[index]['domain'] = operation.domain
    #         index += 1

    #     return operations

    @api.model
    def _get_byproducts_lines(self, *args, **kwargs):
        byproducts = super(ReportBomStructure, self)._get_byproducts_lines(*args, **kwargs)
        bom = args[1]

        index = 0
        for byproduct in bom.byproduct_ids:
            if byproduct._skip_byproduct_line(product):
                continue
            byproducts[index]['domain'] = byproduct.domain

        return byproducts

    @api.model
    def _get_component_data(self, *args, **kwargs):
        component_data = super(ReportBomStructure, self)._get_component_data(*args, **kwargs)
        bom_line = args[2]

        component_data['domain'] = bom_line.domain if bom_line else False
        return component_data
