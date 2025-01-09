### Experiment 1
This experiment takes several hours and up to a few days to complete depending on your HW configuration. For your convenience, our results are already included in folder results and plots.

### Set up
To run the experiment you need:
  · Java 8, we used openjdk version 1.8.0_352
  · Apache Maven 3.6.3
  · Node v16.18.1

Additionally, Java and JavaScript SUTs can install their own dependencies
through Maven and npm respectively, but Python SUTs can't. For this reason we
have added the needed dependencies in the requirements.txt file you find in the
main folder of this package.

### Run the Experiment

* to run the experiment
  ```bash
  python3 evaluate.py
  ```
* to generate the plots (after the experiment has completed without errors)
  ```bash
  python3 generate_plots.py
  ```
``full.json`` and ``short.json`` contain two configurations for this
experiment, the complete one, and a shorter one, respectively. The test folder
of each SUT is specified in the full.json file.

### Recall and Precision Distribution

* to get the plots about the distribution of Recall and Precision
  ```bash
  python3 create_csv.py
  compute_stats.py
  ```
The former script will generate a large csv (``data.csv``) containing all the
data for experiment 1. The latter will generate the ``stats.csv`` file, as well
as a pdf file ``recall_distribution.pdf`` with the plots.
