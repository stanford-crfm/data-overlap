from light_tokenizer import LightTokenizer, DefaultTokenizer
import json
import cattrs
from data_overlap_spec import AggregateOverlapMetric
from light_scenario import ScenarioSpecInstanceIds

def get_tokenizer(normalization) -> LightTokenizer:
    if normalization == "none":
        return LightTokenizer()
    elif normalization == "default":
        return DefaultTokenizer()
    else:
        raise ValueError(f"Normalization strategy {normalization} is not defined.")


def load_aggregate_metrics(file_path: str):
    """Loads aggregate metrics from a newline-delimited JSON file."""
    aggregate_metrics = []
    with open(file_path, 'r') as infile:
        for line in infile:
            try:
                metric_dict = json.loads(line)
                aggregate_metrics.append(cattrs.structure(metric_dict, AggregateOverlapMetric))
            except json.JSONDecodeError as err:
                print(f"Error reading line: {err}")
                continue  # Proceed to next line or handle error as needed
    return aggregate_metrics

def scenario_spec_to_class(scenario_spec) -> str:
#     return scenario_spec.class_name
    return scenario_spec.class_name.split('.')[-1][:-8]


def read_scenario_spec_instance_ids_json():
    scenario_spec_instance_ids_json = 'filtered_scenario_spec_instance_ids.json'
    scenario_spec_instance_ids_jsons = open(scenario_spec_instance_ids_json, "r").readlines()
    return scenario_spec_instance_ids_jsons

def get_scenario_spec_instance_id_dict():
    scenario_spec_instance_ids_jsons = read_scenario_spec_instance_ids_json()
    scenario_spec_instance_id_dict = dict()
    for scenario_spec_instance_ids_json in scenario_spec_instance_ids_jsons:
        scenario_spec_instance_ids_dict = json.loads(scenario_spec_instance_ids_json)
        scenario_spec_instance_ids = cattrs.structure(scenario_spec_instance_ids_dict, ScenarioSpecInstanceIds)
        scenario_spec_instance_id_dict[
            scenario_spec_instance_ids.scenario_spec
        ] = scenario_spec_instance_ids.instance_ids

def get_class_name_to_counts():
    scenario_spec_instance_ids_jsons = read_scenario_spec_instance_ids_json()
    class_name_to_counts = dict()
    scenario_spec_instance_id_dict = dict()
    for scenario_spec_instance_ids_json in scenario_spec_instance_ids_jsons:
        scenario_spec_instance_ids_dict = json.loads(scenario_spec_instance_ids_json)
        scenario_spec_instance_ids = cattrs.structure(scenario_spec_instance_ids_dict, ScenarioSpecInstanceIds)
        scenario_spec_instance_id_dict[
            scenario_spec_instance_ids.scenario_spec
        ] = scenario_spec_instance_ids.instance_ids
        class_name = scenario_spec_to_class(scenario_spec_instance_ids.scenario_spec)
        if class_name not in class_name_to_counts:
            class_name_to_counts[class_name] = 0
        class_name_to_counts[class_name] += len(scenario_spec_instance_ids.instance_ids)
    return class_name_to_counts



def score_to_key(token_score):
    if token_score >= 0.8:
        return 'Dirty'
    elif token_score >= 0.2:
        return 'Clean'
    else:
        return 'Clean'
