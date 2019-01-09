1. Create a new test with one or more questions;

2. In a test question, fill in the *formula* field with some python computation, the values that can be used are:

   * *input_value*: a new field of the inspection line;
   * variables from the previous inspection lines (use the handle to change the order),
     where the variable name is given by the *code* field;

3. Create a new inspection from the test;

4. The inspection lines are recomputed as soon as any field concerning the formula is modified.

   The inspection lines can also be recomputed with the *Compute lines* button in the inspection,
   or the *Compute* button on each line.

Note that formula dependencies can be managed in the new menu *Quality control > Test > Test questions*,
the sequence value will be maintained when the question becomes an inspection.
