### Experiment 3
This experiments takes several hours and up to a few days to complete depending
on your HW configuration. For your convenience, our results are already
included in this folder.

In the next the arguments «sut» and «run» can assume the values:
   «sut» = tensorflow | openjdk
   «run» = python | java | c++ | all

Note that for the openjdk SUT the option python is unavailable because this
language is not used in the implementation of the SUT.

### Run the Experiment

The experiment is composed of several phases each exercised by a script.

* to analyze and count the changes per language in the git history
   ```bash
      python3 count_changes.py «sut»
   ```
   it stores the results in results/«sut»_changes.csv

* to select the best window of commits based on the number of changes per language.
   ```bash
      python3 process_changes.py «sut» «max_aggregation»
   ```
   where «max_aggregation» is an integer and indicates how many commits can be
   squashed together at most. In our experiment we used 20 for tensorflow and
   5 for openjdk.

   It requires results/«sut»_changes.csv to be already computed.
   It stores the results in results/«sut»_consecutive_changes.csv and
   results/«sut»_best_window.json

* to select the commits that will be used in the experiment and updates the
   repo.
   ```bash
      python3 download_repos.py «sut» «k» «delta» «start»
   ```
   For tensorflow we used k=18, delta=15, start=111
   For openjdk we used k=2, delta=0, start=6414

   It requires results/«sut»_consecutive_changes.csv to be already computed.
   It stores the results in results/«sut»_meta.json

* to run the evaluation per SUT and language
   ```bash
      python3 evaluate.py «sut» «run» [history?]
   ```
   where the «history» flag is used for tensorflow to run it on 1000
   consecutive commits.

   It requires results/«sut»_meta.json to be already computed.
   It stores the results in results/«sut»[_history?]_«run».json

* to run the evaluation per a SUT
   ```bash
      python3 run_all.py «sut» [history?]
   ```
   Note that to run:
   ```bash
      python3 run_all.py tensorflow
   ```
   is equivalent to run:
   ```bash
      python3 run_all.py tensorflow python
      python3 run_all.py tensorflow java
      python3 run_all.py tensorflow c++
      python3 run_all.py tensorflow all
   ```
* to analyze the produced results and generate the csv file.
   ```bash
      python3 analyze_results.py «sut» [history?]
   ```
   It requires results/«sut»[_history?]_«run».json to be already computed for
   each run.
   It stores the results in results/«sut»[_history?].csv

### Additional Notes
In the folder results, you can also find the results for the 1,000 commits
execution we only mentioned in the paper but we couldn't add for lack of space.
