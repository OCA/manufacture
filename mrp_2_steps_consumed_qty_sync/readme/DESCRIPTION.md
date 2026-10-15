This module allows to update the quantities consumed from a production
order components when the previous picking in two steps setting is
validated.

In a warehouse that manufactures in two or three steps, components are
moved to the pre-production location with a pick components picking
before they are consumed by the production order. In Odoo core both
documents are independent: the quantities done in the pick components
picking only reserve the goods for the production order, and the
consumed quantities are set again on the production order, either by
hand or in proportion to the bill of materials when the quantity to
produce is set (for example when the first work order is started) or
when a work order is finished.

With this module the pick components picking is the only place where
consumption is reported. The rule is: **what is picked is what is
consumed, and a component that is not picked has not been used**.

- When a pick components picking is validated, the components of the
  production order are reserved with the quantities picked so far, and
  the component demand is updated with the picked quantities plus the
  ones still pending in backorders, without the quantities already taken
  by other backorders of the production order. Quantities set on the
  production order before picking (for example by hand) are replaced by
  the picked ones.
- Setting the quantity to produce (starting a work order, editing the
  quantity to produce or the produced lot in the form) and finishing a
  work order neither consume the components pending to pick nor change
  the picked quantities, also before the first pick components picking
  is validated.
- When the production order is marked as done, the picked quantities
  are consumed, as Odoo core does with the components of manual
  consumption.

Components that do not come from a pick components picking (for example
when the warehouse manufactures in one step) keep the Odoo core behavior.
