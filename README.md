# Data Overlap

## Background
This script computes n-gram overlap between two datasets, generally training and test sets, where the test set are HELM scenarios. After generating n-gram overlap, these results are used to compute metrics, which are aggregated into final results.


## Installation

```bash
# Create a virtual environment.
# Only run this the first time.
python3 -m pip install virtualenv
python3 -m virtualenv -p python3 venv

# Activate the virtual environment.
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

## Generating ngrams

Generally we recommend running the script on a small subset of the train data and a small subset of the test set (the `scenario_data` file in the repo)to ensure the script works correctly. There may need to be minor modifications to ensure that the script correctly parses the training data

For the actual test set, we either run on the [HELM scenarios](https://worksheets.codalab.org/bundles/0x21612363f53c46db8c46795b0f4f17b4), which is a subset of the actual benchmarks, or the benchmarks associated with the HELM scenarios [Benchmark Scenarios](https://worksheets.codalab.org/bundles/0x7a683bf1c1ec43519c1b8b1466ff7bcf). For the latter, the memory consumption is considerable and it is recommended you shard the test data.

For parallelization, we generally just recommend sharding on training and/or test data and running multiple threads in parallel. The results can be easily joined together.

```bash

Usage:

python compute_data_overlap_metrics.py --input-data <input_data> --scenario-data <scenario_data> --output-stats <output_stats> --input-format <input_format>

For instance, you can call this with The Pile, e.g. have:
    input_data  = 00.jsonl (download https://pile.eleuther.ai/)
    scenario_data = (example included with repo, but can use HELM to generate)
    output_stats = arbitrary output file name, e.g. "output_stats"
    input_format = the_pile

If you don't want to output the ngrams that are overlapping in test set to a separate "{output_stats}_ngrams" file, you can pass --no-output-ngrams.

There are additional optional args:
--normalization default 
--tags tag1 tag2
```


## Generating metrics

Run `compute_metrics_from_ngrams.py` to generate metrics. 

`sample_metrics_file` is a file that contains metrics from the pile for testing any script that takes metrics as input.

```
python compute_metrics_from_ngrams.py --ngrams-path 'ngrams_input' --scenario-path 'scenario_data' --out-path 'metrics_output' --filter-path 'filtered_scenarios' --N 13    

    ngrams-path = the ngrams generate from compute_data_overlap_metrics.py
    scenario-data = scenario_data is the same file as used in compute_data_overlap_metrics.py
    out-path = arbitrary output file name, e.g. "output_metrics"
    filter-path = if you want to filter to a subset of the scenarios
    N = n in n-grams
```

## Aggregating metrics

Run `output_aggregate_metrics.py` to aggregate metrics. 
```
python output_aggregate_metrics.py --metrics-path=... --out-path=... 
    metrics-path is the path to the file from compute_metrics_from_ngrams.py
    out-path is an arbitrary output file name
```
