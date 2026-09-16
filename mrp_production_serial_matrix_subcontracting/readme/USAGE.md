1. Configure a subcontracting BoM with a finished product tracked by serial
   number (and optionally components tracked by lot/serial).
2. Create a receipt from the subcontractor partner with the finished product.
3. On the receipt form, click the *Serial Numbers Matrix* button.
4. Select the finished serial numbers and assign component lots/serials in
   the matrix.
5. Click *Validate* to record each subcontracted MO. Backorders are created
   automatically when the receipt has a higher quantity than the serials
   processed.
6. When the matrix finishes, a message is posted on the receipt notifying the
   user who launched the process (useful when the processing runs as a
   queue job in the background).
7. Validate the receipt as usual.
