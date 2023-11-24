In a product template > inventory tab, enable field “Finished product” (note: it can only be enabled for products with variants).

From product template form, use server action “Create finished product structure”: a wizard is displayed with the following fields:

* **Stage name**: this field is used to provide a name to the semi-finished product; the name will be set as *product template name* - *stage name* eg: “Customizable desk (CONFIG) - Wood polishing”

* **Template product**: he semi-finished product will be created as a copy of the product template set in this field, with all the related settings (eg: routes, supplierinfo, product type…).

  Note: only product templates without attributes and values can be set in this field.

* **Attribute(s)**: this field is used to set which attributes and values to copy from finished product to semi-finished product of this stage.

  Note: each semi-finished product cannot have more attributes than the semi-finished product in previous stage.

* **BoM type**: the type of Bom to manufacture the previous product in the semi-finished product chain. If Bom Type = Subcontracting, it’s possible to set subcontractors.

  Note: in first stage, set type of BoM to manufacture finished product; in second stage, set type of BoM to manufacture first stage semi-finished product, and so on.


On creation, a BOM for finished product will be created, with:

* BoM type (and subcontractors) from first line of wizard

* semi-finished product from first line of wizard as “Component (product template)” in BoM lines

* attribute match on semi-finished product attributes.

If a second line was present in wizard, the same will happen for semi-finished product from first line, and so on.
