from light_tokenizer import LightTokenizer, DefaultTokenizer
import json
import cattrs
from data_overlap_spec import AggregateOverlapMetric

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


def score_to_key(token_score):
    if token_score >= 0.8:
        return 'Not Clean'
    elif token_score >= 0.2:
        return 'Not Clean'
    else:
        return 'Clean'
