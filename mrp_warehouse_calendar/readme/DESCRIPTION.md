This module ensures that manufacturing orders created from
procurements respect the calendar assigned to the warehouse
associated with the manufacturing order's picking type.
The planned start date of the manufacturing order is calculated
based on the product's manufacturing lead time and the working
schedules defined in the warehouse calendar.

Additionally, any manual rescheduling of the start or
end date of a manufacturing order will also take the lead
time into account, following the working days defined by
the warehouse calendar.
