This module changes how you manage safety symbols on the Work Center form, allowing for added detail compared to the `mrp_workcenter_safety_symbol` module alone.

**Adding Symbols and Specifications:**

1.  Ensure you have installed the necessary `base_iso7010_data_*` modules.
2.  Navigate to the Manufacturing app.
3.  Go to Configuration > Work Centers.
4.  Open the Work Center record you wish to configure or create a new one.
5.  Click on the "Safety Symbols" tab.
6.  You will see the Kanban display area for safety specifications (the simple M2M view is hidden).
7.  Click the "Create" button (or "Add a line").
8.  A pop-up Form window will appear.
9.  In the "Symbol" field, select the desired `iso7010.symbol` (e.g., "Wear respiratory protection").
10. In the "Specification / Notes" field, enter the specific details required for this symbol at this work center (e.g., "P2 Filter Required", "Change cartridge daily").
11. Click "Save & Close" or "Save & New" on the pop-up form.
12. The entry will appear as a card in the Kanban view on the "Safety Symbols" tab.
13. To edit existing notes, click on the corresponding Kanban card to open the pop-up form again.
14. Click "Save" on the main Work Center form when finished.

The specific instructions are now stored alongside the symbol for this particular Work Center. Other modules can access this data via the `safety_specification_ids` field and its related `specification_notes`.
