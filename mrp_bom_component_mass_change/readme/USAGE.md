You can open the wizard in two ways.

From a bill of materials component line:

1.  Go to *Manufacturing -\> Products -\> Bills of Materials* and open a
    bill of materials.
2.  On the component line you want to change, click the *Mass Change
    Component* button (exchange icon). The component of the line is
    preselected.
3.  In the wizard, review the bills of materials that use the component
    and keep selected only the ones you want to update.
4.  Choose *Replace* and set the new component and the new quantity,
    choose *Remove* to delete the component from the selected bills of
    materials, or choose *Add* to add another component to them.
5.  Click *Apply*.

From the *Manufacturing -\> Operations -\> Mass Change BoM Component*
menu, the wizard opens with no component preselected, so you can freely
choose any component to change and then follow steps 3 to 5 above.

When replacing, the bills of materials that already contain the new
component are automatically removed from the list, so no duplicated
component lines are created. The new quantity is mandatory and is applied
to every updated line.

When adding, set the *Component to Add* and its quantity. The bills of
materials to update can be selected freely, or you can fill in *Bills of
Materials Using* to preload every bill of materials that uses that
component. Bills of materials already containing the component to add are
excluded from the list and are never updated, so no duplicated component
lines are created.

The wizard is also available from any bill of materials components list
view (e.g. the one provided by the module *mrp_bom_component_menu*)
through the *Actions* menu.
