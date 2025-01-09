### BabelRTS replication package

This folder contains:
  · the scripts used in the experiments for BabelRTS (folders experiment_1, experiment_2,experiment_3, and experiment_4)
  · the implementation of BabelRTS (folder babelrts)
  · the data collected and generated plots (inside each experiment folder).

The folder plot_utils contains some code that is used in all experiments.
plot_utils should not be run independently.

### Set up
All the code was tested using Python v3.9 but it should work also with more recent versions.

Both BabelRTS and the SUTs used in the experiment need several additional
modules. For your convenience we have provided a requirements.txt file with all
the needed modules.

Note a couple of empty lines separate the modules needed by BabelRTS and the experiment scripts from those needed by the SUTs. So if you want just to install BabelRTS you can skip the
modules after the empty lines.

We suggest to install it in a virtual environment (as venv) without polluting
your python installation

* to install the dependencies with venv on linux
  ```bash
  cd babelrts_experiments
  python3 -m venv venv
  source venv/bin/activate
  python3 -m pip install -r requirements.txt
  ```
* to install the dependencies without a virtual environment
  ```bash
  python3 -m pip install --user -r requirements.txt
  ```
Additionally, git and an internet connection are required to download the
various revisions for the considered SUTs.

Finally, add the babelrts folder to the PYTHONPATH environment variable. This
is needed to import the BabelRTS modules from the experiment scripts.

### Additional Notes

The whole experiment is quite eager of resources, to run it in all its parts you need:
  · more than 25Gb of free space on disk
  · between 12 hours and few days depending on the computer performances
