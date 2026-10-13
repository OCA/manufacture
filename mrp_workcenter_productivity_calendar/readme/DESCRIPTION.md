Makes work order time tracking duration (Manufacturing Order work order
"Time Tracking" tab) respect the work center's resource calendar instead
of always using the raw elapsed time between the start and end dates.

In Odoo, a work center can have a resource calendar (Working Hours) that
defines the shift and break periods (e.g. 08:00-12:00, lunch 12:00-13:00,
13:00-17:00). Odoo core already uses that calendar to compute duration
for non-productive loss types (blocking reasons), but productive time
-- the normal case for a logged work order activity -- always counts
every wall-clock minute, including breaks. So an activity logged from
10:00 to 14:00 counts as 4 hours even if the work center's calendar has
a 12:00-13:00 lunch break.

This module adds a "Use Calendar for Time Tracking Duration" option on
the work center. When enabled (and a resource calendar is set), the
calendar's shift/break periods are also used to compute productive
time, so breaks configured in the calendar (lunch or otherwise) are
deducted automatically -- consistently with how non-productive loss
types already behave in stock Odoo.

The option is disabled by default, so nothing changes until it is
turned on for a given work center. Work centers without a resource
calendar, or with the option left disabled, keep the native behavior
(raw elapsed time) for productive time.
