Using this module you can have dynamic components of a BOM. It will
allow you to have only 1 line in the BOM if you have hundreds of
attribute values for manufacturing product and hundreds of attributes
values of component (material).

How to use

> 1.  Create a product to produce e.g. Desk.
> 2.  Set 1 attribute (e.g. Color). And select possible values for it.
> 3.  Create a component product (material) e.g. Plastic.
> 4.  Set 1 attribute (Color). And select possible values for it.
> 5.  Create a BOM.
> 6.  Select a manufacturing product Desk.
> 7.  Add a BOM line. Select Component (product template) Plastic.
> 8.  You will see Color attribute appeared in the Apply On Attribute
>     field.
> 9.  Save the BOM.
> 10. Create Manufacturing Order. Select Desk with e.g. Red color to
>     produce and BOM you created.
> 11. You will see in the component list Plastic added with
>     corresponding (red) color.

Consider, that to use this feature component must have only 1 attribute.
And a values of this attribute of a manufacturing product should be
available for a component.
