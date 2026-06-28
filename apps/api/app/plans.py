"""Kamari pricing tiers (demo). Privileges are enforced; no real payments yet.

A plan governs two privileges on the API:
  - rpm: requests per minute (burst rate limit)
  - monthly_quota: age checks per calendar month

Upgrades are a demo: the developer switches plan in-app and the new limits apply
immediately. Wire a payment provider later to gate POST /v1/account/plan.
"""
PLANS: dict[str, dict] = {
    "free": {
        "key": "free", "label": "Free", "price_usd": 0,
        "rpm": 10, "monthly_quota": 1_000,
        "blurb": "For trying Kamari and small projects.",
        "features": ["1,000 age checks / month", "10 requests / minute",
                     "Privacy-first, no images stored", "Community support"],
    },
    "growth": {
        "key": "growth", "label": "Growth", "price_usd": 29,
        "rpm": 60, "monthly_quota": 50_000,
        "blurb": "For growing apps that need more volume.",
        "features": ["50,000 age checks / month", "60 requests / minute",
                     "Multilingual explanations", "Email support"],
    },
    "scale": {
        "key": "scale", "label": "Scale", "price_usd": 199,
        "rpm": 300, "monthly_quota": 500_000,
        "blurb": "For production workloads at scale.",
        "features": ["500,000 age checks / month", "300 requests / minute",
                     "Fairness reporting", "Priority support"],
    },
}
DEFAULT_PLAN = "free"


def plan_for(name: str | None) -> dict:
    return PLANS.get(name or DEFAULT_PLAN, PLANS[DEFAULT_PLAN])
