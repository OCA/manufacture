1. Go to *Manufacturing > Operations > Manufacturing Orders*.
2. Open or create a new Manufacturing Order.
3. Process the order as usual.
4. When you click **Mark as Done**, the module will silently evaluate all active exception rules.
5. If an exception triggers, a wizard will pop up detailing the failed rule(s). 
6. If the rule is not set to *Blocking* and you have the necessary permissions (Exception Manager), you can choose to ignore the exception and proceed. The system will automatically resume the MO completion process.
7. A red banner will display on the MO form view as long as there are unresolved exceptions blocking it.