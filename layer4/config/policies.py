"""
Versioned Configuration — Layer 4 v3.1.1 §6

V0 values (delays, features, thresholds, policies) are versioned
configuration, not hardcoded logic.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class SourcePolicy:
    """Availability policy for a data source."""
    source: str
    delay_minutes: int
    version: str


@dataclass
class FeatureConfig:
    """Feature configuration for a pair."""
    critical: List[str]
    optional: List[str]
    version: str


@dataclass
class TargetConfig:
    """Target configuration."""
    return_type: str  # "log" | "simple"
    price_type: str   # "close" | "open" | "high" | "low"
    threshold: float
    horizon_days: int
    version: str


class ConfigRegistry:
    """Registry for versioned configuration."""
    
    def __init__(self):
        self.source_policies: Dict[str, SourcePolicy] = {}
        self.feature_configs: Dict[str, FeatureConfig] = {}
        self.target_config: Optional[TargetConfig] = None
    
    def register_source_policy(self, policy: SourcePolicy) -> None:
        self.source_policies[policy.source] = policy
    
    def register_feature_config(self, pair: str, config: FeatureConfig) -> None:
        self.feature_configs[pair] = config
    
    def register_target_config(self, config: TargetConfig) -> None:
        self.target_config = config
    
    def get_source_policy(self, source: str) -> Optional[SourcePolicy]:
        return self.source_policies.get(source)
    
    def get_feature_config(self, pair: str) -> Optional[FeatureConfig]:
        return self.feature_configs.get(pair)
    
    def get_target_config(self) -> Optional[TargetConfig]:
        return self.target_config
    
    def to_dict(self) -> Dict:
        return {
            'source_policies': [{'source': p.source, 'delay_minutes': p.delay_minutes, 
                                'version': p.version} for p in self.source_policies.values()],
            'feature_configs': [{'pair': k, 'critical': v.critical, 
                                'optional': v.optional, 'version': v.version} 
                               for k, v in self.feature_configs.items()],
            'target_config': {
                'return_type': self.target_config.return_type if self.target_config else None,
                'price_type': self.target_config.price_type if self.target_config else None,
                'threshold': self.target_config.threshold if self.target_config else None,
                'horizon_days': self.target_config.horizon_days if self.target_config else None,
                'version': self.target_config.version if self.target_config else None
            }
        }


# Default configuration
def create_default_config() -> ConfigRegistry:
    """Create default versioned configuration."""
    registry = ConfigRegistry()
    
    # Source policies
    registry.register_source_policy(SourcePolicy(source='FRED', delay_minutes=2, version='1.0'))
    registry.register_source_policy(SourcePolicy(source='e-Stat', delay_minutes=2, version='1.0'))
    registry.register_source_policy(SourcePolicy(source='Yahoo', delay_minutes=1, version='1.0'))
    
    # Feature configs
    registry.register_feature_config(
        'USDJPY',
        FeatureConfig(
            critical=['us_10y_yield', 'jp_10y_yield', 'usd_jpy_spot'],
            optional=['vix', 'cot_jpy_net', 'usd_inflation', 'jp_inflation'],
            version='1.0'
        )
    )
    registry.register_feature_config(
        'EURUSD',
        FeatureConfig(
            critical=['us_10y_yield', 'eu_10y_yield', 'eur_usd_spot'],
            optional=['vix', 'cot_eur_net', 'usd_inflation', 'eu_inflation'],
            version='1.0'
        )
    )
    
    # Target config
    registry.register_target_config(
        TargetConfig(
            return_type='log',
            price_type='close',
            threshold=0.0,
            horizon_days=5,
            version='1.0'
        )
    )
    
    return registry
