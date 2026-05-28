The alignment check runs automatically — no manual configuration is required.

**Warning banner**

Open any Manufacturing Order that is not yet done or cancelled. If the MO's
components, quantities, or consumed-in-operation assignments no longer match
the linked BoM (for example, because the BoM was updated after the MO was
confirmed), a yellow warning banner is displayed at the top of the form
explaining what is out of sync.

**Confirmation dialog**

When confirming a draft MO whose components or quantities are not aligned with
the BoM, a dialog is shown with three options:

- **Update MO and Confirm** — re-syncs the MO with the current BoM (equivalent
  to the standard *Update BoM* action) and then confirms it. Use this when the
  BoM change is intentional and the MO should reflect it.
- **Confirm Anyway** — confirms the MO as-is, ignoring the misalignment.
- **Go Back** — closes the dialog and returns to the MO so it can be reviewed
  or manually corrected before confirming.
