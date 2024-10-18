Using this module you can have dynamic components of a BOM.
It will allow you to have only 1 line in the BOM if you have hundreds of attribute
values for manufacturing product and hundreds of attributes values of component (material).

How to use

 #. Create a product to produce e.g. Desk.
 #. Set 1 attribute (e.g. Color). And select possible values for it.
 #. Create a component product (material) e.g. Plastic.
 #. Set 1 attribute (Color). And select possible values for it.
 #. Create a BOM.
 #. Select a manufacturing product Desk.
 #. Add a BOM line. Select Component (product template) Plastic.
 #. You will see Color attribute appeared in the Apply On Attribute field.
 #. Save the BOM.
 #. Create Manufacturing Order. Select Desk with e.g. Red color to produce and BOM you created.
 #. You will see in the component list Plastic added with corresponding (red) color.

Consider, that to use this feature component must have only 1 attribute.
And a values of this attribute of a manufacturing product should be available for a component.
