"""Analytics literals: feature names for adoption tracking."""

# Critical features for Adoption Rate widget (used in dashboard and track_feature_usage).
FEATURE_AI_ANALYSIS = 'ai_analysis'
FEATURE_SHARE_LINK_CREATE = 'share_link_create'
FEATURE_ANALYTICS_DASHBOARD = 'analytics.asset_bank'

# All adoption-tracked features (for dashboard aggregation).
FEATURE_ADOPTION_NAMES = (
    FEATURE_AI_ANALYSIS,
    FEATURE_SHARE_LINK_CREATE,
    FEATURE_ANALYTICS_DASHBOARD,
)
