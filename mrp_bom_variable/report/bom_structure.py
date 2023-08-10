from odoo import api, models


class BomStructureReport(models.AbstractModel):
    _inherit = "report.mrp.report_bom_structure"

    @api.model
    def _get_pdf_line(
        self, bom_id, product_id=False, qty=1, child_bom_ids=None, unfolded=False
    ):
        """Call _get_bom_array_lines()"""
        res = super()._get_pdf_line(bom_id, product_id, qty, child_bom_ids, unfolded)
        line_ids = self.env["mrp.bom.line"].search([("bom_id", "=", bom_id)])
        for line in res["lines"]:
            line_id = line_ids.filtered(
                lambda l: l.condition and l.product_id.display_name == line["name"]
            )
            line["condition"] = line_id.condition or ""
        return res

    @api.model
    def _get_bom_array_lines(
        self, data, level, unfolded_ids, unfolded, parent_unfolded=True
    ):
        """Called by _get_pdf_line()"""
        res = super()._get_bom_array_lines(data, level, unfolded_ids, unfolded, True)
        return res

    @api.model
    def _get_component_data(
        self,
        parent_bom,
        warehouse,
        bom_line,
        line_quantity,
        level,
        index,
        product_info,
        ignore_stock=False,
    ):
        """Called by _get_bom_data()"""
        data = super()._get_component_data(
            parent_bom,
            warehouse,
            bom_line,
            line_quantity,
            level,
            index,
            product_info,
            ignore_stock=ignore_stock,
        )
        data = self._complete_bom_variable_report(data)
        return data

    def _complete_bom_variable_report(self, data):
        # TODO only for variable report
        data["lo"] = "1"
        return data

    @api.model
    def _get_bom_data(
        self,
        bom,
        warehouse,
        product=False,
        line_qty=False,
        bom_line=False,
        level=0,
        parent_bom=False,
        index=0,
        product_info=False,
        ignore_stock=False,
    ):
        """Allow to add values to main object (Bom header)"""
        res = super()._get_bom_data(
            bom,
            warehouse,
            product=product,
            line_qty=line_qty,
            bom_line=bom_line,
            level=level,
            parent_bom=parent_bom,
            index=index,
            product_info=product_info,
            ignore_stock=ignore_stock,
        )
        return res
