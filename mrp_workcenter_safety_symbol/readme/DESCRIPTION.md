This module allows associating standard ISO 7010 safety symbols with Manufacturing Work Centers in Odoo.

## Overview

This module provides the basic functionality to link predefined ISO 7010 safety symbols (managed via the `base_iso7010` module and populated by `base_iso7010_data_*` modules) to specific Manufacturing Work Centers (`mrp.workcenter`).

Features:

* Adds a 'Safety Symbols' tab to the Work Center form view.
* Provides a Many2many field (`safety_symbol_ids`) to link `mrp.workcenter` records to `iso7010.symbol` records.
* Displays selected symbols visually using a Kanban view within the tab.
