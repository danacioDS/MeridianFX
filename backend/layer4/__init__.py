"""
LAYER 4: DATA LAYER

MISSION:
Given a timestamp T, demonstrate exactly what information
was available to Meridian at T.

DOMAIN INVARIANTS (7):
PIT-1: available_time <= T
PIT-2: derived.available_time = max(inputs.available_time)
PIT-3: vintage_selection = max(vintage_time) WHERE available_time <= T
PIT-4: NO interpolation (AS-OF JOIN only)
PIT-5: All timestamps timezone-aware (UTC)
PIT-6: prediction_timestamp < target_start < target_end
PIT-7: event_time <= release_time <= source_available_time <= system_available_time

LINEAGE:
Structured references sufficient to reconstruct the exact provenance
of a feature, without duplicating source observations.

VERSIONED CONFIGURATION:
V0 values (delays, features, thresholds, policies) are versioned
configuration, not hardcoded logic.
"""
