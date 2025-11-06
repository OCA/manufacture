Quality tests now support auto-compute formulas on qualitative or quantitative questions. Enable "Auto-compute" on a question to open the Python editor and define code that sets the `result` variable (and optionally `message`).

The bundled template lists the evaluation context (line, inspection, test, question, env, and safe helpers). Assign a number to `result` for quantitative lines or return an answer name/boolean for qualitative ones; set `message` when you want an entry appended to the inspection internal notes.
