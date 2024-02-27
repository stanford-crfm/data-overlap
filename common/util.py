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


def read_scenario_spec_instance_ids_json(test_only=True):
    if test_only:
        scenario_spec_instance_ids_json = 'filtered_scenario_data_new_test_only_ids'
    else:
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
    return scenario_spec_instance_id_dict

def get_class_name_to_counts(test_only=True):
    scenario_spec_instance_ids_jsons = read_scenario_spec_instance_ids_json(test_only)
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

def get_dataset_to_counts(test_only=True):
    scenario_spec_instance_ids_jsons = read_scenario_spec_instance_ids_json(test_only)
    dataset_name_to_counts = dict()
    scenario_spec_instance_id_dict = dict()
    for scenario_spec_instance_ids_json in scenario_spec_instance_ids_jsons:
        scenario_spec_instance_ids_dict = json.loads(scenario_spec_instance_ids_json)
        scenario_spec_instance_ids = cattrs.structure(scenario_spec_instance_ids_dict, ScenarioSpecInstanceIds)
        scenario_spec_instance_id_dict[
            scenario_spec_instance_ids.scenario_spec
        ] = scenario_spec_instance_ids.instance_ids
        class_name = scenario_spec_to_dataset_name(scenario_spec_instance_ids.scenario_spec)
        if class_name not in dataset_name_to_counts:
            if class_name == 'Copyright':
                continue
            dataset_name_to_counts[class_name] = 0
        dataset_name_to_counts[class_name] += len(scenario_spec_instance_ids.instance_ids)
    return dataset_name_to_counts

def scenario_spec_to_dataset_name(scenario_spec):
    """ Get the dataset name from scenario_spec """
    class_name = scenario_spec.class_name.split('.')[-1][:-8]  # Get only the class name, not the full module path
    key = mapping[class_name]
    
    args = scenario_spec.args  # ScenarioSpec args
    
    
    if len(key) == 1:
        return key[0]
    
    dataset = args['dataset_name'] if 'dataset_name' in args else args['dataset']
    key = dataset_mapping[dataset]
    return key


def score_to_key(token_score):
    if token_score >= 0.8:
        return 'Dirty'
    elif token_score >= 0.2:
        return 'Clean'
    else:
        return 'Clean'

mapping = {
    "BabiQA": ["bAbI"],
    "BBQ": ["BBQ"],
    "BLiMP": ["BLiMP"],
    "BOLD": ["BOLD"],
    "BoolQ": ["BoolQ"],
    "CivilComments": ["CivilComments"],
    "Code": ["HumanEval", "APPS"],
    'Copyright':['Copyright'],
    "CommonSense": ["CommonSenseQA", "HellaSwag", "PIQA", "SIQA"], 
    "Disinformation": ["Disinformation - HELM"],
    "DyckLanguage": ["DyckLanguage"],
    "EntityDataImputation": ["EntityDataImputation"],
    "EntityMatching": ["EntityMatching"],
    "GSM8K": ["GSM8K"],
    "ICE": ["ICE"],
    "IMDB": ["IMDB"],
    "LegalSupport": ["LegalSupport"],
    "LSAT": ["LSAT"],
    "MATH": ["MATH"],
    "MMLU": ["MMLU"],
    "MSMARCO": ["MS MARCO"],
    "NarrativeQA": ["NarrativeQA"],
    "NaturalQA": ["Natural Questions"],
    "QuAC": ["QuAC"],
    "RAFT": ["RAFT"],
    "RealToxicityPrompts": ["RealToxicityPrompts"],
    "Summarization": ["XSum", "CNN/Daily Mail"],
    "SyntheticEfficiency": ["SyntheticEfficiency"],
    "SyntheticReasoning": ["SyntheticReasoning"],
    "SRN": ["SynetheticReasoningNatural"],
    "ThePile": ["The Pile"],
    "TruthfulQA": ["TruthfulQA"],
    "TwitterAAE": ["TwitterAAE"],
    "WIKIFact": ["WikiFact"]
}
dataset_mapping = {
    "humaneval": "HumanEval",
    "apps": "APPS",
    "xsum-sampled": "XSum",
    "cnn-dm": "CNN/Daily Mail",
    'hellaswag': 'HellaSwag',
    'openbookqa': 'OpenBookQA',
}

def scenario_spec_to_dataset_name(scenario_spec):
    """ Get the dataset name from scenario_spec """
    try:
        class_name = scenario_spec.class_name.split('.')[-1][:-8]  # Get only the class name, not the full module path
        key = mapping[class_name]
        
        args = scenario_spec.args  # ScenarioSpec args
        
        
        if len(key) == 1:
            return key[0]
        
        dataset = args['dataset_name'] if 'dataset_name' in args else args['dataset']
        key = dataset_mapping[dataset]
        return key
    except Exception as e:
        print(e)
        return 'NA'