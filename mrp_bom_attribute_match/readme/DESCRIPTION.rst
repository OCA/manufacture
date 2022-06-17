This module addresses the BoM case where the product to manufacture has one attribute with tens or hundreds of values (usually attribute "color", eg: "Configurable Desk" can be produced in 900 different colors).

Creating a dynamic BoM currently requires adding one BoM line for each attribute value to match component variant with attribute value (eg: component "Desk board (Green)" to be applied to variant "Green").

This has 3 downsides:

- BoM lines proliferation (more error prone)

- Difficult to update in case a new attribute value (new color paint) is added

- Difficult to update in case base component changes.


This module allows to use a product template as component in BoM lines, automatically matching component variant to use in MO line with the attribute value selected for manufacture.

Eg: Product template "Desk Board" is added to BoM line for product "Configurable Desk"; match is made on attribute "Color". In MO, if product to manufacture is "Configurable Desk (Steel, Pink)", MO line will have component "Desk Board (Pink)".

Using the same BoM, if product to manufacture is "Configurable Desk (Steel, Yellow)", MO line will have component "Desk Board (Yellow)".


The flow is valid also if the Component (Product Template) has more than one attribute matching the product to manufacture; in this case, on MO line the component variant will be the one matching multiple attribute values for the product to manufacture.


Various checks are in place to make sure this flow is not disrupted:

- user cannot add a product in field "Component (Product Template)" which:

    does not have matching attributes with product to manufacture

    has a different variant-generating attribute than the product to manufacture

- Adding a new variant-generating attribute to a product used as "Component (Product Template)" raises an error if the attribute is not included in all the products to manufacture where component is referenced.

- Removing an attribute used for BoM attribute matching from product to manufacture raises an error.

- On a BoM line with Component (Product Template) set, an attribute value of attributes referenced in "Match on attribute" field cannot be used in field "Apply to variant".

- If attribute value for matching attribute in manufactured product is not present in component (product template), the BoM line is skipped in MO.
