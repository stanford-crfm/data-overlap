from common.object_spec import ObjectSpec

class ScenarioSpec(ObjectSpec):
    pass

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
    class_name = scenario_spec.class_name.split('.')[-1][:-8]  # Get only the class name, not the full module path
    key = mapping[class_name]
    
    args = scenario_spec.args  # ScenarioSpec args
    
    
    if len(key) == 1:
        return key[0]
    
    dataset = args['dataset_name'] if 'dataset_name' in args else args['dataset']
    key = dataset_mapping[dataset]
    return key

def get_dataset_to_counts():
    dataset_to_counts = dict()
    scenario_spec_instance_id_dict = dict()
    scenario_spec_instance_ids_json = 'filtered_scenario_spec_instance_ids.json'
    scenario_spec_instance_ids_jsons = open(scenario_spec_instance_ids_json, "r").readlines()
    for scenario_spec_instance_ids_json in scenario_spec_instance_ids_jsons:
        scenario_spec_instance_ids_dict = json.loads(scenario_spec_instance_ids_json)
        scenario_spec_instance_ids = cattrs.structure(scenario_spec_instance_ids_dict, ScenarioSpecInstanceIds)
        scenario_spec_instance_id_dict[
            scenario_spec_instance_ids.scenario_spec
        ] = scenario_spec_instance_ids.instance_ids
        dataset_name = scenario_spec_to_dataset_name(scenario_spec_instance_ids.scenario_spec)
        if dataset_name not in dataset_to_counts:
            if dataset_name == 'Copyright':
                continue
    #         print(scenario_spec_instance_ids_json)
            dataset_to_counts[dataset_name] = 0
        dataset_to_counts[dataset_name] += len(scenario_spec_instance_ids.instance_ids)
