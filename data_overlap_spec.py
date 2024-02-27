from dataclasses import dataclass
from typing import List, Tuple
from enum import Enum


try:
    from light_scenario import LightScenarioKey, LightInstance
except Exception:
    from helm.benchmark.data_overlap.light_scenario import LightScenarioKey, LightInstance


@dataclass(frozen=True)
class GroupOverlapStats:
    """
    Dataclass that represents group data overlap stats
    e.g.
    {
        "group": "natural_qa_closedbook",
        "num_instances": 2144,
        "num_overlapping_inputs": 1,
        "num_overlapping_references": 100
    }
    """

    group: str

    num_instances: int

    num_overlapping_inputs: int

    num_overlapping_references: int

    @property
    def overlapping_input_ratio(self):
        return self.num_overlapping_inputs / self.num_instances

    @property
    def overlapping_reference_ratio(self):
        return self.num_overlapping_references / self.num_instances


@dataclass(frozen=True)
class OverlapProtocolSpec:
    """Specification for how we compute overlap"""

    # the N of the n_grams we're running
    n: int


@dataclass(frozen=True)
class DataOverlapStatsKey:
    """Dataclass that represents output data overlap stats"""

    light_scenario_key: LightScenarioKey

    overlap_protocol_spec: OverlapProtocolSpec


@dataclass(frozen=True)
class DataOverlapStats:
    """Dataclass that represents output data overlap stats"""

    data_overlap_stats_key: DataOverlapStatsKey

    num_instances: int

    instance_ids_with_overlapping_input: List[str]

    instance_ids_with_overlapping_reference: List[str]


@dataclass(frozen=True)
class EntryDataOverlapKey:
    """Unique key representing either the input or references of a single instance in a scenario."""

    stats_key: DataOverlapStatsKey
    part: str
    """Either PART_INPUT or PART_REF"""
    instance_id: str


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

@dataclass(frozen=True)
class AggregateDataOverlapKey:
    """Key representing the aggregated data overlap stats"""
    stats_key: DataOverlapStatsKey
    part: str

@dataclass(frozen=True)
class AggregateOverlapMetric:
    """Dataclass representing the aggregated overlap metrics"""
    aggregate_data_overlap_key: AggregateDataOverlapKey
    metric_scores: List[float]  # List of scores instead of a single value
    metric_protocol_spec: MetricProtocolSpec


@dataclass(frozen=True)
class AnnotatedOverlapPart:
    """
    Dataclass annotates a given scenario entry with overlaps
    """
    
    part: str
        
    annotated_entry_overlap: List[Tuple[str, int]]
    """list of (word, count) where (word, count) is the 13-gram that starts with word"""
        
    metrics : List[OverlapMetric]

@dataclass(frozen=True)
class TotalAnnotatedEntryOverlap:
    """
    Dataclass annotates a given scenario entry with overlaps
    """
    instance: LightInstance
        
    stats_key: DataOverlapStatsKey
        
    instance_id: str
        
        
    annotated_input_overlap: AnnotatedOverlapPart
    """list of (word, count) where (word, count) is the 13-gram that starts with word"""

    annotated_ref_overlap: AnnotatedOverlapPart
    """list of (word, count) where (word, count) is the 13-gram that starts with word"""

