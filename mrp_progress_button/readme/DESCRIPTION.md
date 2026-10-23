This module adds an *Unstart* button on Manufacturing Orders to move
them from *In Progress* back to *Confirmed*, and a *Started On* date
that records when the Manufacturing Order was actually started.

Since 19.0, the actual start date is stored in a dedicated *Started On*
field instead of overwriting the scheduled date of the Manufacturing Order.
