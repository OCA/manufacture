## Usage

This module introduces a workflow to manage subcontracting operations
at work order level through a dedicated wizard.

### 1. Triggering the flow

The process starts from the **"Variation" wizard**, which can be launched
by selecting one or more work orders.

This wizard allows the responsible user to decide how the subcontracting
operation should be handled.

---

### 2. Choosing the subcontracting strategy

Inside the wizard, the user can choose between two main approaches:

#### A. Purchase Order flow
- Generate one or multiple Purchase Orders (PO) for subcontractors
- This is the standard structured flow

#### B. Direct shipment (urgent flow)
- Skip Purchase Order creation
- Directly generate outgoing transfers (OUT) to subcontractors

This option is intended for urgent scenarios where speed is required.

---

### 3. Handling multiple subcontractors

The system supports multiple subcontractors for the same operation.

This allows:
- parallel processing
- supplier competition (multiple vendors working on the same task)

---

### 4. Purchase Order flow behavior

When using the Purchase Order flow:

- After confirming the PO, outgoing transfers (OUT) are generated

Optionally:
- It is possible to prepare the incoming flow even before validating
  the first OUT, already at PO confirmation

---

### 5. Logistics flow

#### Outgoing (OUT)
- Materials are sent to the subcontractor
- OUT transfer is validated

#### Incoming (IN)
- Finished or processed goods are received back
- IN transfer is generated:
  - automatically after OUT validation, or
  - earlier if enabled in PO confirmation

---

### 6. Completion of the work order phase

The work order is considered completed when:

- All related incoming transfers (IN) are validated

At this point:
- the subcontracted operation is fully completed
- the workflow proceeds to the next step

---

### Notes

- The workflow is flexible and supports both structured and urgent flows
- It enhances traceability between subcontracted operations and work orders
- It is designed for hybrid production scenarios involving external suppliers
