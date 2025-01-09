### Experiment 4

This experiments takes several hours and up to a few days to complete depending
on your HW configuration. For your convenience, our results are already
included in this folder.

### Run the Experiment

* install defects4j https://github.com/rjust/defects4j

* clone BugsInPy into this folder https://github.com/soarsmu/BugsInPy

* clone BugsJS into this folder https://github.com/BugsJS/bug-dataset

* to evaluate fault detection on Java SUTs
    ```bash
    python3 evaluate_java.py
    ```

* to evaluate fault detection on Python SUTs
    ```bash
    python3 evaluate_python.py
    ```

* to evaluate fault detection on JavaScript SUTs
    ```bash
    python3 evaluate_javascript.py
    ```

* to generate the plots
    ```bash
    python3 generate_plots.py
    ```
