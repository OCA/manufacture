To use this module, you need to:

1.  Go to *Manufacturing \> Manufacturing Requests*.
2.  Create a manufacturing request or open a existing one (assigned to
    you or created from a procurement).
3.  If you click on *Request approval* button the user assigned as
    approver will be added to the thread.
4.  If you are the approver you can either click on *Approve* or
    *Reject* buttons.
5.  Rejecting a MR will cancel it and propagate this cancellation to
    destination moves.
6.  Approving a MR will allow you to create manufacturing orders.
7.  You can manually set to done a request by clicking in the button
    *Done*.

To create MOs from MRs you have to:

1.  Go to approved manufacturing request.
2.  Click on the button *Create Manufacturing Order*.
3.  In the opened wizard, click on *Compute lines* so you will have a
    quantity proposed for creating a MO. This quantity is the maximum
    quantity you can produce with the current stock available for the
    components needed in the source location.
4.  Use the proposed quantity or change it and click on *Create MO* at
    the bottom of the wizard.

**NOTE:** This module does not restrict the quantity that can be
converted from a MR to MOs. It is in hands of the user to decide when a
MR is ended and to set it to *Done* state.
