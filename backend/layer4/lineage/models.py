"""
Lineage models — Layer 4 v3.1.1 §5

Structured references sufficient to reconstruct the exact provenance
of a feature.
"""
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class SourceReference:
    """Reference to a source observation."""
    observation_id: str
    source: str
    series_name: str
    reference_period: str
    vintage_id: str
    vintage_time: datetime
    available_time: datetime


@dataclass
class LineageReference:
    """Reference to another lineage record."""
    lineage_id: str
    role: str  # "input" | "source"


@dataclass
class LineageRecord:
    """
    Complete lineage record for a feature.
    
    Purpose:
    - Audit: Trace the origin of any feature
    - Debugging: Identify problems in the derivation chain
    - Reproducibility: Reconstruct exact generation conditions
    - Explainability: Explain to the user where each signal comes from
    - Data Quality: Detect anomalies in the provenance chain
    - Research Reproducibility: Reproduce exactly the dataset used
    """
    lineage_id: str
    feature_id: str
    feature_version: str
    derivation_function: Optional[str]
    input_references: List[LineageReference]
    source_references: List[SourceReference]
    available_time: datetime
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'lineage_id': self.lineage_id,
            'feature_id': self.feature_id,
            'feature_version': self.feature_version,
            'derivation_function': self.derivation_function,
            'input_references': [{'lineage_id': r.lineage_id, 'role': r.role} 
                                for r in self.input_references],
            'source_references': [{
                'observation_id': s.observation_id,
                'source': s.source,
                'series_name': s.series_name,
                'reference_period': s.reference_period,
                'vintage_id': s.vintage_id,
                'vintage_time': s.vintage_time.isoformat(),
                'available_time': s.available_time.isoformat()
            } for s in self.source_references],
            'available_time': self.available_time.isoformat(),
            'created_at': self.created_at.isoformat()
        }


class LineageRegistry:
    """Registry for lineage records."""
    
    def __init__(self):
        self.records: Dict[str, LineageRecord] = {}
    
    def register(self, record: LineageRecord) -> None:
        self.records[record.lineage_id] = record
    
    def get(self, lineage_id: str) -> Optional[LineageRecord]:
        return self.records.get(lineage_id)
    
    def get_by_feature(self, feature_id: str) -> List[LineageRecord]:
        return [r for r in self.records.values() if r.feature_id == feature_id]
    
    def get_available_at(self, timestamp: datetime) -> List[LineageRecord]:
        return [r for r in self.records.values() 
                if r.available_time <= timestamp]
