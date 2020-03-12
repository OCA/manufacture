Odoo has a limitation on tracked product's components
which are not manufactured in the ERP.

When you try to do it, you get this warning:

Some of your components are tracked, you have to specify a manufacturing order in order to retrieve the correct components.

Unfortunately, it doesn't cover all the use cases.

Example:
You receive eggs and you want to unbuild them in 2 parts:

    - yellow part
    - white part

Each of the parts are tracked and not linked to a previous manufacturing order
because, you don't build the eggs yourself, you subcontract it to a chicken.
