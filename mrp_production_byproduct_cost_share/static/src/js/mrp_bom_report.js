odoo.define("mrp_production_byproduct_cost_share.mrp_bom_report", function (require) {
    "use strict";

    var MrpBomReport = require("mrp.mrp_bom_report");

    MrpBomReport.include({
        get_byproducts: function (event) {
            var self = this;
            var $parent = $(event.currentTarget).closest("tr");
            var activeID = $parent.data("bom-id");
            var qty = $parent.data("qty");
            var level = $parent.data("level") || 0;
            var total = $parent.data("total") || 0;
            return this._rpc({
                model: "report.mrp.report_bom_structure",
                method: "get_byproducts",
                args: [activeID, parseFloat(qty), level + 1, parseFloat(total)],
            }).then(function (result) {
                self.render_html(event, $parent, result);
            });
        },
    });
});
