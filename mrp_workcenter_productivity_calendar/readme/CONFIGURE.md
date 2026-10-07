Go to Manufacturing > Configuration > Work Centers, open a work center
and:

1. Set its "Working Hours" field to a resource calendar that has the
   shift and break periods you want applied (e.g. 08:00-12:00,
   13:00-17:00, with the 12:00-13:00 gap as the lunch break).
2. Enable "Use Calendar for Time Tracking Duration" (only visible once
   a calendar is set).

Any period not covered by the calendar's attendance lines -- lunch,
overnight, weekends, etc. -- is treated as non-working time and is not
counted in the duration.

Work centers left without a resource calendar, or with the option
disabled, are not affected: their productive time keeps counting the
raw elapsed time, as in stock Odoo.

Productive/performance time is deducted using the exact same
calculation core Odoo already uses for non-productive loss types
(blocking reasons), so no new timezone or leave-handling behavior is
introduced: naive dates are treated as UTC and resource-specific
leaves (e.g. planned downtime recorded against the work center) are
taken into account the same way in both cases.

**Check the calendar's Timezone field.** The shift hours (e.g.
08:00-12:00) are interpreted in the timezone set on the resource
calendar itself (Working Hours screen), shown with a mismatch warning
if it differs from your browser's timezone. If that field is wrong --
e.g. left at a default that does not match where the work center
actually operates -- the computed duration will be off by the
difference between the two timezones. Set it explicitly instead of
relying on the default.
