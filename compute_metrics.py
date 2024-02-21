from data_overlap_spec import DataOverlapStatsKey, EntryOverlapNgrams, OverlapMetric, MetricProtocolSpec, PartialOverlapSpec, FrequencySpec, EntryOverlapMetric
from collections import defaultdict
import ast
from nltk import ngrams


def compute_binary_overlap(instance_str, overlapping_ngram_counts, tokenizer, frequency = 0):
    """ 
    Compute  binary overlap
    If pass in frequency, include only the ngrams with count <= frequency
    """
    tokens = tokenizer.tokenize(instance_str)
    ngram_counts_dict = defaultdict(int)

    # construct a dict of ngram -> count
    for ngram, count in overlapping_ngram_counts:
        ngram = tuple(ast.literal_eval(ngram))
        ngram_counts_dict[ngram] = count

    metric_score = 0

    for ngram in ngrams(tokens, 13):
        count = ngram_counts_dict[ngram]
        if frequency == 0 or count <= frequency:
            if count != 0:
                metric_score = 1
                break

    overlap_metric = OverlapMetric(
        metric_score = metric_score,
        metric_protocol_spec = MetricProtocolSpec(
            partial_overlap_spec = PartialOverlapSpec.binary,
            frequency_spec = FrequencySpec(
                filter_value = frequency,
                weighting = False
            )
        )
    )

    return overlap_metric

def compute_jaccard_overlap(instance_str, overlapping_ngram_counts, tokenizer, frequency = 0):
    """ 
    Compute weighted and unweighted jaccard overlap
    If pass in frequency, include only the ngrams with count <= frequency
    """
    tokens = tokenizer.tokenize(instance_str)
    ngram_counts_dict = defaultdict(int)

    # construct a dict of ngram -> count
    for ngram, count in overlapping_ngram_counts:
        ngram = tuple(ast.literal_eval(ngram))
        ngram_counts_dict[ngram] = count

    total_ngram_count = 0
    counts = 0
    weighted_score = 0

    for ngram in ngrams(tokens, 13):
        count = ngram_counts_dict[ngram]
        if frequency == 0 or count <= frequency:
            if count != 0:
                counts += 1
                weighted_score += 1 / count
        total_ngram_count += 1

    unweighted_score = counts / total_ngram_count
    weighted_score = weighted_score / total_ngram_count

    unweighted_overlap_metric = OverlapMetric(
        metric_score = unweighted_score ,
        metric_protocol_spec = MetricProtocolSpec(
            partial_overlap_spec = PartialOverlapSpec.jaccard,
            frequency_spec = FrequencySpec(
                filter_value = frequency,
                weighting = False
            )
        )
    )

    weighted_overlap_metric = OverlapMetric(
        metric_score = weighted_score ,
        metric_protocol_spec = MetricProtocolSpec(
            partial_overlap_spec = PartialOverlapSpec.jaccard,
            frequency_spec = FrequencySpec(
                filter_value = frequency,
                weighting = True
            )
        )
    )

    return unweighted_overlap_metric, weighted_overlap_metric

# Token overlap
def compute_token_overlap(instance_str, overlapping_ngram_counts, tokenizer, frequency = 0):
    """ 
    Compute weighted and unweighted token overlap
    If pass in frequency, include only the ngrams with count <= frequency
    """
    tokens = tokenizer.tokenize(instance_str)
    ngram_counts_dict = defaultdict(int)

    # construct a dict of ngram -> count
    for ngram, count in overlapping_ngram_counts:
        ngram = tuple(ast.literal_eval(ngram))
        ngram_counts_dict[ngram] = count

    total_token_count = 0
    counts = 0
    weighted_score = 0
    weight = 0
    token_budget = 0

    for ngram in ngrams(tokens, 13):
        curr_count = ngram_counts_dict[ngram]

        # either no frequency, or check current count is less than frequency
        # or a previous contiguous count (weight != 0) less than frequency
        if frequency == 0 or curr_count <= frequency or (weight != 0 and weight <= frequency):
            if curr_count != 0:
                token_budget = 13
                if weight > 0:
                    weight = min(curr_count, weight)
                else:
                    weight = curr_count 

        if token_budget > 0:
            token_budget -= 1
            counts += 1
            weighted_score += 1 / weight
        else:
            weight = 0
        total_token_count += 1

    for token in ngram[1:]:
        if token_budget > 0:
            token_budget -= 1
            counts += 1
            weighted_score += 1 / weight
        total_token_count += 1

    unweighted_score = counts / total_token_count
    weighted_score = weighted_score / total_token_count

    unweighted_overlap_metric = OverlapMetric(
        metric_score = unweighted_score ,
        metric_protocol_spec = MetricProtocolSpec(
            partial_overlap_spec = PartialOverlapSpec.token,
            frequency_spec = FrequencySpec(
                filter_value = frequency,
                weighting = False
            )
        )
    )

    weighted_overlap_metric = OverlapMetric(
        metric_score = weighted_score ,
        metric_protocol_spec = MetricProtocolSpec(
            partial_overlap_spec = PartialOverlapSpec.token,
            frequency_spec = FrequencySpec(
                filter_value = frequency,
                weighting = True
            )
        )
    )

    return unweighted_overlap_metric, weighted_overlap_metric

def compute_and_add_metrics(instance_str, overlapping_ngram_counts, tokenizer, entry_data_overlap_key, entry_overlap_metric_list, frequency = 0):
    overlap_metric = compute_binary_overlap(instance_str, overlapping_ngram_counts, tokenizer, frequency)
    binary_metric = EntryOverlapMetric(entry_data_overlap_key=entry_data_overlap_key, overlap_metric=overlap_metric)
    entry_overlap_metric_list.append(binary_metric)

    unweighted_overlap_metric, weighted_overlap_metric = compute_jaccard_overlap(instance_str, overlapping_ngram_counts, tokenizer, frequency)
    unweighted_jaccard = EntryOverlapMetric(entry_data_overlap_key=entry_data_overlap_key, overlap_metric=unweighted_overlap_metric)
    weighted_jaccard = EntryOverlapMetric(entry_data_overlap_key=entry_data_overlap_key, overlap_metric=weighted_overlap_metric)
    entry_overlap_metric_list.append(unweighted_jaccard)
    entry_overlap_metric_list.append(weighted_jaccard)

    unweighted_overlap_metric, weighted_overlap_metric = compute_token_overlap(instance_str, overlapping_ngram_counts, tokenizer, frequency)
    unweighted_token = EntryOverlapMetric(entry_data_overlap_key=entry_data_overlap_key, overlap_metric=unweighted_overlap_metric)
    weighted_token = EntryOverlapMetric(entry_data_overlap_key=entry_data_overlap_key, overlap_metric=weighted_overlap_metric)
    entry_overlap_metric_list.append(unweighted_token)
    entry_overlap_metric_list.append(weighted_token)


