This experiments takes several hours and up to a few days to complete. For your convenience, our results are already included in this folder.

<sut> = tensorflow | openjdk
<run> = python | java | c++ | all
<sut> == opendk && <run> == python = False



The scripts contained in this folder are:


count_changes.py <sut>
analyzes the git history of the sut and counts the changes in each language.
Stores the result sin results/<sut>_changes.csv



process_changes.py <sut> <max_aggregation>
Selects the best window of commits to used during the experiment base on the changes in each language.
<max_aggregation> is an integer and indicates how many commits can be squashed together at most.
In our experiment we used 20 for tensorflow and 5 for openjdk.
Requires results/<sut>_changes.csv to be already computed.
Stores the results in results/<sut>_consecutive_changes.csv and results/<sut>_best_window.json



download_repos.py <sut> <k> <delta> <start>
Selectes the commits that will be used in the experiment and updates the repo.
For tensorflow we used k=18, delta=15, start=111
For openjdk we used k=2, delta=0, start=6414
Requires results/<sut>_consecutive_changes.csv to be already computed.
Stores the results in results/<sut>_meta.json



evaluate.py <sut> <run> [history?]
Runs one run on one sut.
The <history> flag is used for tensorflow to run it on 1000 consecutive commits.
Requires results/<sut>_meta.json to be already computed.
Stores the results in results/<sut>[_history?]_<run>.json



run_all.py <sut> [history?]
Runs all runs on a sut.
"run_all.py tensorflow" is equivalent to:
evaluate.py tensorflow python
evaluate.py tensorflow java
evaluate.py tensorflow c++
evaluate.py tensorflow all



analyze_results.py <sut> [history?]
analyzed the results produced by run_all.py or by evaluate.py and produces a csv file.
Requires results/<sut>[_history?]_<run>.json to be already computed for each run.
Stores the results in results/<sut>[_history?].csv