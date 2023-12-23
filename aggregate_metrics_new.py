path = 'metrics/filtered_pile_metrics_all'

import ast
import json
import cattrs
import pandas as pd
from enum import Enum
import numpy
from nltk import ngrams
from collections import defaultdict
from typing import List, Tuple
from dataclasses import dataclass

from data_overlap_spec import DataOverlapStats, DataOverlapStatsKey, EntryOverlapNgrams
from compute_data_overlap_metrics import load_light_scenarios_from_jsonl
from common.util import get_tokenizer
from common.general import asdict_without_nones

@dataclass(frozen=True)
class EntryDataOverlapKey:
    """Unique key representing either the input or references of a single instance in a scenario."""

    stats_key: DataOverlapStatsKey
    part: str
    """Either PART_INPUT or PART_REF"""
    instance_id: str


# Input: List[EntryOverlapNgrams]
@dataclass(frozen=True)
class EntryOverlapNgrams:
    """Dataclass that represents output data overlap stats"""

    entry_data_overlap_key: EntryDataOverlapKey

    overlapping_ngram_counts: List[Tuple[str, int]]


class PartialOverlapSpec(int, Enum):
    binary = 0
    jaccard = 1
    token = 2
    def __str__(self):
        return self.name

@dataclass(frozen=True)
class FrequencySpec:
    # Filter ngrams with frequency >= filter_value; 0 means no filter
    filter_value: int
    # Whether to apply weight; we'll do inverse frequency
    weighting: bool
        
@dataclass(frozen=True)
class MetricProtocolSpec:
    """Specification for how we compute the metric"""
    
    partial_overlap_spec: PartialOverlapSpec
    frequency_spec: FrequencySpec
        
@dataclass(frozen=True)
class OverlapMetric:
    metric_score: float # use 0/1 for binary, can revise as neded
    metric_protocol_spec: MetricProtocolSpec

# Output: List[EntryOverlapMetric]
@dataclass(frozen=True)
class EntryOverlapMetric:
    """Dataclass that represents output data overlap stats"""

    entry_data_overlap_key: EntryDataOverlapKey

    overlap_metric: OverlapMetric

def scenario_spec_to_class(scenario_spec) -> str:
    return f"{'.'.join(scenario_spec.class_name.split('.')[-1:])}"     

overlap_metrics_jsons = open(path, "r").readlines()

entry_overlap_metric_list = []
for entry_overlap_metric_json in overlap_metrics_jsons:
    entry_overlap_metric_dict = json.loads(entry_overlap_metric_json)
    entry_overlap_metric_list.append(cattrs.structure(entry_overlap_metric_dict, EntryOverlapMetric))
    
# Initialize an empty dictionary to store the mapping
score_dict = {}

# Iterate through the entry_overlap_metric_list
for entry_overlap_metric in entry_overlap_metric_list:
    light_scenario_key = entry_overlap_metric.entry_data_overlap_key.stats_key.light_scenario_key

    metric_protocol_spec = entry_overlap_metric.overlap_metric.metric_protocol_spec
    metric_score = entry_overlap_metric.overlap_metric.metric_score
    part = entry_overlap_metric.entry_data_overlap_key.part
    
    key = (light_scenario_key, part)
    # Check if the scenario_spec already exists in the dictionary
    if key not in score_dict:
        score_dict[key] = {}
    
    # Check if the metric_protocol_spec is already a key under scenario_spec
    if metric_protocol_spec not in score_dict[key]:
        score_dict[key][metric_protocol_spec] = []
    
    # Append the metric_score to the list associated with metric_protocol_spec under scenario_spec
    score_dict[key][metric_protocol_spec].append(metric_score)

def metric_to_label(metric: MetricProtocolSpec) -> str:
    partial_overlap_str = str(metric.partial_overlap_spec)
    frequency_str = f"{metric.frequency_spec.filter_value} {metric.frequency_spec.weighting}"
    return f"{partial_overlap_str}, {frequency_str}"


def light_scenario_key_to_str(light_scenario_key) -> str:
    scenario_spec = light_scenario_key.scenario_spec
    class_name_str = f"{'.'.join(scenario_spec.class_name.split('.')[-2:])}"
    args_str = f"{{{', '.join([f'{k}: {v}' for k, v in scenario_spec.args.items()])}}}"
    split = light_scenario_key.split
    return f"{class_name_str}, {args_str}, {split}"


PART_INPUT: str = "input"
PART_REF: str = "reference"
metric_protocol_specs_list  = [
    MetricProtocolSpec(PartialOverlapSpec.binary, FrequencySpec(0, False)),
    MetricProtocolSpec(PartialOverlapSpec.jaccard, FrequencySpec(0, False)),
    MetricProtocolSpec(PartialOverlapSpec.jaccard, FrequencySpec(0, True)),
    MetricProtocolSpec(PartialOverlapSpec.token, FrequencySpec(0, False)),
    MetricProtocolSpec(PartialOverlapSpec.token, FrequencySpec(0, True)),
    MetricProtocolSpec(PartialOverlapSpec.binary, FrequencySpec(10, False)),
    MetricProtocolSpec(PartialOverlapSpec.jaccard, FrequencySpec(10, False)),
    MetricProtocolSpec(PartialOverlapSpec.jaccard, FrequencySpec(10, True)),
    MetricProtocolSpec(PartialOverlapSpec.token, FrequencySpec(10, False)),
    MetricProtocolSpec(PartialOverlapSpec.token, FrequencySpec(10, True))
]

cols = ['light_scenario_key', 'part']
res = []
scenario_spec_to_results = defaultdict(dict)
light_scenario_key_to_str(light_scenario_key)
def stats_to_row(key, metric_scores):
    light_scenario_key, part = key
    light_scenario_key_str = light_scenario_key_to_str(light_scenario_key)
    for metric_spec, values in metric_scores.items():
        scenario_spec_to_results[key][metric_spec] = sum(values)
    ret = [light_scenario_key_str, part, ]
    for metric_spec in metric_protocol_specs_list:
        ret.append(scenario_spec_to_results[key][metric_spec])
    return ret


for metric_spec in metric_protocol_specs_list:
    cols.append(metric_to_label(metric_spec))

for class_name, metric_scores in score_dict.items():
    res.append(stats_to_row(class_name, metric_scores))

agg_metrics_df = pd.DataFrame(res, columns=cols)
agg_metrics_df.to_csv('the_pile_metrics_class_new.csv', index=False)
    