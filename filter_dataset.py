import cattrs
import json
from data_overlap_spec import DataOverlapStats, EntryOverlapNgrams
from common.util import get_scenario_spec_instance_id_dict, scenario_spec_to_dataset_name
from collections import defaultdict

output_path = 'data/output_stats_pile_all'
ngram_path =  'data/output_stats_pile_ngrams_all2'

output_stats_jsons = open(output_path, "r").readlines()

# create dict of DataOverlapStatsKey -> output_stats full_stats_dict = dict()
full_stats_dict = dict()

data_overlap_stats_list = []
for output_stats_json in output_stats_jsons:
    output_stats_dict = json.loads(output_stats_json)
    data_overlap_stats_list.append(cattrs.structure(output_stats_dict, DataOverlapStats))

for data_overlap_stats in data_overlap_stats_list:
    data_overlap_stats_key = data_overlap_stats.data_overlap_stats_key
    full_stats_dict[data_overlap_stats_key] = data_overlap_stats

scenario_spec_instance_id_dict = get_scenario_spec_instance_id_dict()

entry_overlap_ngrams_list = []

ngram_jsons = open(ngram_path, "r").readlines()
for ngram_json in ngram_jsons:
    if len(ngram_json) == 1:
        continue
    try:
        entry_overlap_ngrams = json.loads(ngram_json)
    except Exception as e:
        print('hi')
        print(e)
        print(ngram_json)
        print(len(ngram_json))
        continue
    try:
        entry_overlap_ngrams = cattrs.structure(entry_overlap_ngrams, EntryOverlapNgrams)
        scenario_spec = entry_overlap_ngrams.entry_data_overlap_key.stats_key.light_scenario_key.scenario_spec
        split = entry_overlap_ngrams.entry_data_overlap_key.stats_key.light_scenario_key.split
        if scenario_spec not in scenario_spec_instance_id_dict:
            continue
        instance_ids = scenario_spec_instance_id_dict[scenario_spec]
        if entry_overlap_ngrams.entry_data_overlap_key.instance_id not in instance_ids:
            continue
        else:
            entry_overlap_ngrams_list.append(entry_overlap_ngrams)
    except Exception as e:
        print('hi2')
        print(e)
        print(entry_overlap_ngrams)
        print(ngram_json)
        print(len(ngram_json))
        continue

from common.general import asdict_without_nones
with open(f"data/filtered_pile_ngrams", "w") as f:
    for entry_overlap_ngrams in entry_overlap_ngrams_list:
        f.write(f"{json.dumps(asdict_without_nones(entry_overlap_ngrams))}\n")
with open(f"data/filtered_pile_ngrams_test_only", "w") as f:
    for entry_overlap_ngrams in entry_overlap_ngrams_list:
        part = entry_overlap_ngrams.entry_data_overlap_key.part
        scenario_spec = entry_overlap_ngrams.entry_data_overlap_key.stats_key.light_scenario_key.scenario_spec
        split = entry_overlap_ngrams.entry_data_overlap_key.stats_key.light_scenario_key.split
        if split != 'test':
            continue
        f.write(f"{json.dumps(asdict_without_nones(entry_overlap_ngrams))}\n")
with open(f"data/filtered_pile_ngrams_test_13_only", "w") as f:
    for entry_overlap_ngrams in entry_overlap_ngrams_list:
        part = entry_overlap_ngrams.entry_data_overlap_key.part
        scenario_spec = entry_overlap_ngrams.entry_data_overlap_key.stats_key.light_scenario_key.scenario_spec
        split = entry_overlap_ngrams.entry_data_overlap_key.stats_key.light_scenario_key.split
        if split != 'test':
            continue
        
        n = entry_overlap_ngrams.entry_data_overlap_key.stats_key.overlap_protocol_spec.n
        if n != 13:
            continue
        f.write(f"{json.dumps(asdict_without_nones(entry_overlap_ngrams))}\n")