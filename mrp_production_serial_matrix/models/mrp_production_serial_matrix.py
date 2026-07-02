# Copyright 2021-24 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from collections import defaultdict

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero


class MrpProductionSerialMatrix(models.Model):
    _name = "mrp.production.serial.matrix"
    _inherit = "mail.thread"
    _description = "Mrp Production Serial Matrix"
    _rec_name = "production_id"

    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("in_progress", "In Progress"),
            ("exception", "Exception"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        string="Status",
        required=True,
        readonly=True,
        copy=False,
        tracking=True,
        default="draft",
    )
    production_id = fields.Many2one(
        comodel_name="mrp.production",
        string="Manufacturing Order",
        readonly=True,
        ondelete="cascade",
    )
    production_state = fields.Selection(
        related="production_id.state",
        string="MO Status",
    )
    product_id = fields.Many2one(
        related="production_id.product_id",
        readonly=True,
    )
    company_id = fields.Many2one(
        related="production_id.company_id",
        readonly=True,
    )
    finished_lot_ids = fields.Many2many(
        string="Finished Product Serial Numbers",
        comodel_name="stock.lot",
        domain="[('product_id', '=', product_id)]",
    )
    line_ids = fields.One2many(
        string="Matrix Cell",
        comodel_name="mrp.production.serial.matrix.line",
        inverse_name="wizard_id",
    )
    lot_selection_warning_msg = fields.Char(compute="_compute_lot_selection_warning")
    lot_selection_warning_ids = fields.Many2many(
        comodel_name="stock.lot", compute="_compute_lot_selection_warning"
    )
    lot_selection_warning_count = fields.Integer(
        compute="_compute_lot_selection_warning"
    )
    include_lots = fields.Boolean(
        string="Include Lots?",
        help="Include products tracked by Lots in matrix. Product tracket by "
        "serial numbers are always included.",
    )

    def unlink(self):
        for matrix in self:
            if matrix.state in ["done", "in_progress", "cancel"]:
                raise UserError(
                    _(
                        "You cannot delete a serial matrix that is in progress, "
                        "done or cancelled."
                    )
                )
        return super().unlink()

    def action_cancel_matrix(self):
        self.ensure_one()
        if self.production_id.state not in ("done", "cancel"):
            raise UserError(
                _(
                    "The matrix can only be cancelled when the related MO is "
                    "done or cancelled."
                )
            )
        if self.state in ("done", "cancel"):
            raise UserError(_("The matrix is already %s.") % self.state)
        self.state = "cancel"
        self.message_post(
            body=_(
                "Matrix manually cancelled. The related MO (%(mo)s) is in state "
                "'%(state)s'."
            )
            % {"mo": self.production_id.name, "state": self.production_id.state}
        )

    def action_reset_to_draft(self):
        self.ensure_one()
        if self.state != "exception":
            raise UserError(
                _("Only matrices in 'Exception' state can be reset to 'Draft'.")
            )
        pg = self.production_id.procurement_group_id
        if pg:
            related_mos = pg.mrp_production_ids
            pending_mos = related_mos.filtered(
                lambda m: m.state not in ("done", "cancel")
            )
            processed_lots = related_mos.filtered(lambda m: m.state == "done").mapped(
                "lot_producing_id"
            )
        else:
            pending_mos = self.production_id.filtered(
                lambda m: m.state not in ("done", "cancel")
            )
            processed_lots = self.env["stock.lot"]
        if not pending_mos:
            raise UserError(
                _(
                    "There is no pending MO related to this matrix. Cancel the "
                    "matrix instead."
                )
            )
        pending_mo = pending_mos[:1]
        remaining_lots = self.finished_lot_ids - processed_lots
        self.production_id = pending_mo
        self.line_ids.unlink()
        matrix_lines = self._get_matrix_lines(pending_mo, remaining_lots)
        self.write(
            {
                "finished_lot_ids": [(6, 0, remaining_lots.ids)],
                "line_ids": [(0, 0, x) for x in matrix_lines],
                "state": "draft",
            }
        )
        self.message_post(
            body=_(
                "Matrix reset to 'Draft'. Pending MO: %(mo)s. Remaining serial "
                "numbers to process: %(lots)s."
            )
            % {
                "mo": pending_mo.name,
                "lots": ", ".join(remaining_lots.mapped("name")) or "—",
            }
        )

    @api.depends("line_ids", "line_ids.component_lot_id")
    def _compute_lot_selection_warning(self):
        for rec in self:
            warning_lots = self.env["stock.lot"]
            warning_msgs = []
            # Serials:
            serial_lines = rec.line_ids.filtered(
                lambda line: line.component_id.tracking == "serial"
            )
            serial_counter = {}
            for sl in serial_lines:
                if not sl.component_lot_id:
                    continue
                serial_counter.setdefault(sl.component_lot_id, 0)
                serial_counter[sl.component_lot_id] += 1
            for lot, counter in serial_counter.items():
                if counter > 1:
                    warning_lots += lot
                    warning_msgs.append(
                        "Serial number %s selected several times" % lot.name
                    )
            # Lots
            lot_lines = rec.line_ids.filtered(
                lambda line: line.component_id.tracking == "lot"
            )
            lot_consumption = {}
            for ll in lot_lines:
                if not ll.component_lot_id:
                    continue
                lot_consumption.setdefault(ll.component_lot_id, 0)
                free_qty, reserved_qty = ll._get_available_and_reserved_quantities()
                available_quantity = free_qty + reserved_qty
                if (
                    available_quantity - lot_consumption[ll.component_lot_id]
                    < ll.lot_qty
                ):
                    warning_lots += ll.component_lot_id
                    warning_msgs.append(
                        f"Lot {ll.component_lot_id.name} not available at the "
                        f"needed qty ({available_quantity}/{ll.lot_qty})"
                    )
                lot_consumption[ll.component_lot_id] += ll.lot_qty

            not_filled_lines = rec.line_ids.filtered(
                lambda line: line.finished_lot_id and not line.component_lot_id
            )
            if not_filled_lines:
                not_filled_finshed_lots = not_filled_lines.mapped("finished_lot_id")
                warning_lots += not_filled_finshed_lots
                warning_msgs.append(
                    f"Some cells are not filled for some finished serial number "
                    f"({', '.join(not_filled_finshed_lots.mapped('name'))})"
                )
            rec.lot_selection_warning_msg = ", ".join(warning_msgs)
            rec.lot_selection_warning_ids = warning_lots
            rec.lot_selection_warning_count = len(warning_lots)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            production_id = vals.get("production_id", False)
            if not production_id:
                raise UserError(
                    _("Context propagation: The production order was not propagated.")
                )
            production = self.env["mrp.production"].browse(production_id)
            if not production.show_serial_matrix:
                raise UserError(
                    _(
                        "The finished product of this MO is not "
                        "tracked by serial numbers."
                    )
                )
            finished_lots = self.env["stock.lot"]
            if production.lot_producing_id:
                finished_lots = production.lot_producing_id
            matrix_lines = self._get_matrix_lines(production, finished_lots)
            vals.update(
                {
                    "line_ids": [(0, 0, x) for x in matrix_lines],
                    "finished_lot_ids": [
                        (4, lot_id, 0) for lot_id in finished_lots.ids
                    ],
                }
            )
        return super().create(vals_list)

    def _get_matrix_lines(self, production, finished_lots):
        tracked_components = []
        for move in production.move_raw_ids:
            rounding = move.product_id.uom_id.rounding
            if float_is_zero(move.product_qty, precision_rounding=rounding):
                # Component moves cannot be deleted in in-progress MO's; however,
                # they can be set to 0 units to consume. In such case, we ignore
                # the move.
                continue
            boml = move.bom_line_id
            # TODO: UoM (MO/BoM using different UoMs than product's defaults).
            if boml:
                qty_per_finished_unit = boml.product_qty / boml.bom_id.product_qty
            else:
                # The product could have been added for the specific MO but not
                # be part of the BoM.
                qty_per_finished_unit = move.product_qty / production.product_qty
            if move.product_id.tracking == "serial":
                for i in range(1, int(qty_per_finished_unit) + 1):
                    tracked_components.append((move.product_id, i, 1))
            elif move.product_id.tracking == "lot" and self.include_lots:
                tracked_components.append((move.product_id, 0, qty_per_finished_unit))

        matrix_lines = []
        current_lot = False
        new_lot_number = 0
        for _i in range(int(production.product_qty)):
            if finished_lots:
                current_lot = finished_lots[0]
            else:
                new_lot_number += 1
            for component_tuple in tracked_components:
                line = self._prepare_matrix_line(
                    component_tuple, finished_lot=current_lot, number=new_lot_number
                )
                matrix_lines.append(line)
            if current_lot:
                finished_lots -= current_lot
                current_lot = False
        return matrix_lines

    def _prepare_matrix_line(self, component_tuple, finished_lot=None, number=None):
        component, lot_no, lot_qty = component_tuple
        column_name = component.display_name
        if lot_no > 0:
            column_name += " (%s)" % lot_no
        res = {
            "component_id": component.id,
            "component_column_name": column_name,
            "lot_qty": lot_qty,
        }
        if finished_lot:
            if isinstance(finished_lot.id, models.NewId):
                # NewId instances are not handled correctly later, this is a
                # small workaround. In future versions it might not be needed.
                lot_id = finished_lot.id.origin
            else:
                lot_id = finished_lot.id
            res.update(
                {
                    "finished_lot_id": lot_id,
                    "finished_lot_name": finished_lot.name,
                }
            )
        elif isinstance(number, int):
            res.update(
                {
                    "finished_lot_name": _("(New Lot %s)") % number,
                }
            )
        return res

    @api.onchange("finished_lot_ids", "include_lots")
    def _onchange_finished_lot_ids(self):
        for rec in self:
            matrix_lines = self._get_matrix_lines(
                rec.production_id,
                rec.finished_lot_ids,
            )
            rec.line_ids = False
            rec.write({"line_ids": [(0, 0, x) for x in matrix_lines]})

    def button_validate(self):
        self.ensure_one()
        if self.lot_selection_warning_count > 0:
            raise UserError(
                _("Some issues has been detected in your selection: %s")
                % self.lot_selection_warning_msg
            )
        if self.production_id.state == "done":
            self.state = "exception"
            raise UserError(_("The MO (%s) is already done.") % self.production_id.name)
        self.state = "in_progress"
        self._process_serial_matrix()

    def _get_matrix_lines_map(self):
        mapping = defaultdict(lambda: self.env["mrp.production.serial.matrix.line"])
        for line in self.line_ids:
            fp_key = line.finished_lot_id.id or line.finished_lot_name
            comp_key = line.component_id.id
            mapping[(fp_key, comp_key)] += line
        return mapping

    def call_next_process_serial_matrix_lot(
        self, mos, lots_to_process=None, current_mo=False
    ):
        self._process_serial_matrix_lot(
            mos, lots_to_process=lots_to_process, current_mo=current_mo
        )

    def _process_serial_matrix_lot(self, mos, lots_to_process=None, current_mo=False):
        matrix_map = self._get_matrix_lines_map()
        fp_lot = lots_to_process[0] if len(lots_to_process) > 1 else lots_to_process
        if not fp_lot:
            self._set_matrix_done()
            return mos
        try:
            self._prepare_mo_for_serial(current_mo, fp_lot)
            self._process_component_moves(current_mo, fp_lot, matrix_map)
            mos += current_mo
            current_mo = self._validate_and_get_backorder(current_mo)
            if current_mo:
                return self.call_next_process_serial_matrix_lot(
                    mos, lots_to_process=lots_to_process - fp_lot, current_mo=current_mo
                )
            self._set_matrix_done()
        except UserError as e:
            self._set_matrix_exception(str(e))
        return mos

    def _set_matrix_done(self):
        self.state = "done"
        self.message_post(body=_("The serial matrix finished successfully"))

    def _set_matrix_exception(self, error):
        self.state = "exception"
        self.message_post(body=_("Error during the processing: %s") % error)

    def _process_serial_matrix(self):
        mos = self.env["mrp.production"]
        current_mo = self.production_id
        mos = self._process_serial_matrix_lot(
            mos, lots_to_process=self.finished_lot_ids, current_mo=current_mo
        )
        return mos

    def _prepare_mo_for_serial(self, mo, fp_lot):
        mo.lot_producing_id = fp_lot
        mo.qty_producing = 1.0
        mo._set_qty_producing()

    def _process_component_moves(self, mo, fp_lot, matrix_map):
        for move in mo.move_raw_ids:
            if float_is_zero(
                move.product_qty, precision_rounding=move.product_uom.rounding
            ):
                continue
            if move.product_id.tracking in ["serial", "lot"]:
                lines = matrix_map.get((fp_lot.id, move.product_id.id))
                if not lines and fp_lot.name:
                    pass
                if lines:
                    self._amend_reservations(move, lines)
                    self._consume_selected_lots(move, lines)
                elif move.product_id.tracking == "lot" and not self.include_lots:
                    move.picked = True

    def _validate_and_get_backorder(self, mo):
        res = mo.button_mark_done()
        backorder_wizard_model = self.env["mrp.production.backorder"]
        if (
            isinstance(res, dict)
            and res.get("res_model") == backorder_wizard_model._name
        ):
            context = res.get("context", {})
            wizard = backorder_wizard_model.with_context(**context).create({})
            wizard.action_backorder()
            pending_mos = mo.procurement_group_id.mrp_production_ids.filtered(
                lambda m: m.state not in ["done", "cancel"]
            )
            return pending_mos[0] if pending_mos else False
        if isinstance(res, dict):
            raise UserError(
                f"Something went wrong and the MO could not be validated. {res}"
            )
        return False

    def _amend_reservations(self, move, matrix_lines):
        lots_desired = matrix_lines.mapped("component_lot_id")
        current_lines = move.move_line_ids.filtered(lambda ml: ml.lot_id)
        lots_current = current_lines.mapped("lot_id")
        to_remove = lots_current - lots_desired
        if to_remove:
            current_lines.filtered(lambda ml: ml.lot_id in to_remove).unlink()
        to_add = lots_desired - lots_current
        for lot in to_add:
            if move.product_id.tracking == "serial":
                qty_needed = 1.0
            else:
                qty_needed = sum(matrix_lines.mapped("lot_qty"))
            self._reserve_lot_in_move(move, lot, qty=qty_needed)
        return True

    def _consume_selected_lots(self, move, matrix_lines):
        lots_in_matrix = matrix_lines.mapped("component_lot_id")
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for ml in move.move_line_ids:
            if ml.lot_id in lots_in_matrix:
                ml.picked = True
            elif float_is_zero(ml.quantity, precision_digits=precision):
                ml.unlink()
            else:
                ml.lot_id = lots_in_matrix[0] if len(lots_in_matrix) > 1 else False
                ml.picked = True

    def _reserve_lot_in_move(self, move, lot, qty):
        precision_digits = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        available_quantity = self.env["stock.quant"]._get_available_quantity(
            move.product_id,
            move.location_id,
            lot_id=lot,
        )
        if (
            float_compare(available_quantity, 0.0, precision_digits=precision_digits)
            <= 0
        ):
            raise ValidationError(
                _("Serial/Lot number '%s' not available at source location.") % lot.name
            )
        move._update_reserved_quantity(
            qty,
            move.location_id,
            lot_id=lot,
            strict=True,
        )
