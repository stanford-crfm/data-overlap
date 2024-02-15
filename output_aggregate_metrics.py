import argparse
import json
import cattrs
import pandas as pd
import numpy
from nltk import ngrams
from collections import defaultdict
from typing import List, Tuple, Any
from dataclasses import dataclass

from data_overlap_spec import AggregateOverlapMetric, AggregateDataOverlapKey, MetricProtocolSpec, PartialOverlapSpec, FrequencySpec, EntryOverlapMetric
from compute_data_overlap_metrics import load_light_scenarios_from_jsonl
from common.util import get_tokenizer
from common.general import asdict_without_nones

def scenario_spec_to_class(scenario_spec) -> str:
    return f"{'.'.join(scenario_spec.class_name.split('.')[-1:])}"     

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


non_weighted_metrics = [
    MetricProtocolSpec(PartialOverlapSpec.binary, FrequencySpec(0, False)),
    MetricProtocolSpec(PartialOverlapSpec.jaccard, FrequencySpec(0, False)),
    MetricProtocolSpec(PartialOverlapSpec.token, FrequencySpec(0, False)),
]


def aggregate_metrics(path, out_path):
    overlap_metrics_jsons = open(path, "r").readlines()

    entry_overlap_metric_list = []
    for entry_overlap_metric_json in overlap_metrics_jsons:
        entry_overlap_metric_dict = json.loads(entry_overlap_metric_json)
        entry_overlap_metric_list.append(cattrs.structure(entry_overlap_metric_dict, EntryOverlapMetric))

    # Initialize a new dictionary for aggregated scores
    aggregate_score_dict = {}

    for entry_overlap_metric in entry_overlap_metric_list:
        # Extract necessary information
        stats_key = entry_overlap_metric.entry_data_overlap_key.stats_key
        part = entry_overlap_metric.entry_data_overlap_key.part
        metric_protocol_spec = entry_overlap_metric.overlap_metric.metric_protocol_spec
        if metric_protocol_spec not in non_weighted_metrics:
            continue
        metric_score = entry_overlap_metric.overlap_metric.metric_score

        # Define the aggregate key
        agg_key = (stats_key, part, metric_protocol_spec)

        # Initialize or append the metric score
        if agg_key not in aggregate_score_dict:
            if stats_key.light_scenario_key.scenario_spec.class_name == 'helm.benchmark.scenarios.copyright_scenario.CopyrightScenario':
                continue
            aggregate_score_dict[agg_key] = [metric_score]
        else:
            aggregate_score_dict[agg_key].append(metric_score)

    # Convert the aggregated data to AggregateOverlapMetric objects
    aggregate_overlap_metrics = []
    for (stats_key, part, metric_protocol_spec), scores in aggregate_score_dict.items():
        aggregate_key = AggregateDataOverlapKey(
            stats_key=stats_key,
            part=part
        )
        if aggregate_key.stats_key.light_scenario_key.split == 'test':
            aggregate_overlap_metrics.append(
                AggregateOverlapMetric(
                    aggregate_data_overlap_key=aggregate_key,
                    metric_scores=scores,
                    metric_protocol_spec=metric_protocol_spec
                )
            )

    def save_metrics_to_jsonl(overlap_metrics: List[AggregateOverlapMetric], filename: str):
        with open(filename, "w") as f:
            for overlap_metric in overlap_metrics:
                f.write(json.dumps(asdict_without_nones(overlap_metric), ensure_ascii=False) + "\n")
    
    save_metrics_to_jsonl(aggregate_overlap_metrics, out_path)

def get_args() -> Any:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics-path", type=str, required=True, help="Path to your metrics")
    parser.add_argument("--out-path", type=str, required=True, help="Path to the output metrics file")
    return parser.parse_args()

if __name__ == "__main__":
    args = get_args()

    aggregate_metrics(args.metrics_path, args.out_path)
