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

## Input training data
Depending on your training data format, you may need to update [load_documents.py](https://github.com/stanford-crfm/data-overlap/blob/main/load_documents.py) to support that training data format.

## Generating ngrams

Generally we recommend running the script on a small subset of the train data and a small subset of the test set (the `scenario_data` file in the repo)to ensure the script works correctly. There may need to be minor modifications to ensure that the script correctly parses the training data

For the actual test set, we either run on the [HELM scenarios](https://worksheets.codalab.org/bundles/0x21612363f53c46db8c46795b0f4f17b4), which is a subset of the actual benchmarks, or the benchmarks associated with the HELM scenarios [Benchmark Scenarios](https://worksheets.codalab.org/bundles/0x7a683bf1c1ec43519c1b8b1466ff7bcf). For the latter, the memory consumption is considerable and it is recommended you shard the test data.

For parallelization, we generally just recommend sharding on training and/or test data and running multiple threads in parallel. The results can be easily joined together.

```bash

Usage:


python compute_data_overlap_metrics.py --input-data <input_data> --scenario-data <scenario_data> --output-stats <output_stats> --input-format <input_format>

For instance, you can call this with The Pile, e.g. have:
    input_data  = pile_input.json (download more at https://pile.eleuther.ai/)
    scenario_data = (example included with repo, but can use HELM to generate)
    output_stats = arbitrary output file name, e.g. "output_stats"
    input_format = the_pile

This will output two files: <output_stats> and <output_stats_ngrams>. Pass the second ngrams file to the later steps.

There are additional optional args:
--normalization default 
--tags tag1 tag2

```
Example: 

We run the example on `example_input.jsonl` as the sample training data and `scenario_data` as the example scenario data; both are in the repo.

```
python compute_data_overlap_metrics.py --input-data ./example_input.jsonl --scenario-data ./scenario_data --output-stats output_stats --input-format the_pile --N 13

-> produces "output_stats" and "output_stats_ngrams". "output_stats_ngrams" will be the input for the next example stage. These outputs are also in the repo if you want to directly run these
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
Example: 
We take the input `output_stats_ngrams` from the last step (or directly from the repo) and run

```
python compute_metrics_from_ngrams.py --ngrams-path output_stats_ngrams --scenario-path scenario_data --out-path metrics_output --N 13    
-> produces metrics_output file for next step
```


## Aggregating metrics

Run `output_aggregate_metrics.py` and `output_aggregate_metrics_both.py` to aggregate metrics. 
```
python output_aggregate_metrics.py --metrics-path=... --out-path=... 
    metrics-path is the path to the file from compute_metrics_from_ngrams.py
    out-path is an arbitrary output file name
```
Example: 
We take the input `metrics_output` from the last step (or directly from the repo) and run

```
python output_aggregate_metrics.py --metrics-path metrics_output --out-path aggregate_metrics
python output_aggregate_metrics_both.py --metrics-path metrics_output --out-path aggregate_metrics_both

-> produces aggregate metrics output, aggregate_metrics and aggregate_metrics_both
```


