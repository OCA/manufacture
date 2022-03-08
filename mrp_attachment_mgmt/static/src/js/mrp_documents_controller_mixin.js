odoo.define("mrp_attachment_mgmt.controllerMixin", function (require) {
    "use strict";
    var MrpDocumentsKanbanController = require("mrp.MrpDocumentsKanbanController");
    MrpDocumentsKanbanController.include({
        renderButtons: function () {
            const context = this.model.get(this.handle).getContext();
            if (!context.hide_upload) {
                this._super(...arguments);
            }
        },
    });
});
