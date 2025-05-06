This module enhances the `mrp_workcenter_safety_symbol` module by allowing users to add specific textual notes or specifications for each safety symbol linked to a Manufacturing Work Center.

## Overview

This module builds upon `mrp_workcenter_safety_symbol` to provide a more detailed way of managing safety requirements on Work Centers.

Features:

* Introduces an intermediate model (`mrp.workcenter.safety.specification`) to store the link between Work Center, Symbol, and Notes.
* Replaces the simple Kanban symbol selection view on the Work Center's "Safety Symbols" tab with a list view (rendered as Kanban cards) where specifications can be managed via pop-up forms.
* Allows adding details like required PPE grade (e.g., "P2 filter"), specific checks, or other instructions directly related to a symbol for that specific work center, managed via pop-up forms.
