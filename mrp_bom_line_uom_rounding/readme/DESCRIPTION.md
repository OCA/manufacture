This module enforces Unit of Measure (UoM) rounding validation on Bill of Materials (BoM) component quantities.

When a component is added to a BoM, the system validates that the quantity respects the rounding precision defined in the Unit of Measure. For example, if a UoM has a rounding of 1.0 (like "Units" or "Each"), the system will not allow quantities like 0.1 or 0.5.

This prevents data inconsistencies where users could enter quantities that don't make sense for the given UoM, such as 0.1 pieces when the UoM is configured for whole units only.
