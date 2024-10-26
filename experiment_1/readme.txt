This experiments takes several hours and up to a few days to complete. For your convenience, our results are already included in this folder.

Run evaluate.py to run the experiment.
Run generate_plots.py after the experiment has completed without errors.
full.json and short.json contian 2 configurations for this experiment, the complete one, and a shorter one, respectively.

Other dependencies for this experiment:
- openjdk version "1.8.0_352"
- Apache Maven 3.6.3
- Node v16.18.1

Additionally, Java and JavaScript suts are able to install their own dependencies through Maven and npm respectively, but Python suts are not.
Not all Python suts contain a requirements.txt file. So installing all dependencies for all python SUTs cannot be easily automated.
For each Python sut, we recommend going into the root folder, and running "python3.9 -m pytest <test_folder>". This will reveal any missing dependency.
The test folder of each sut is specified in the full.json file.