"""Email delivery via the live n8n "Dynamic Email Template Sender" workflow.

The gateway never sends mail itself. It POSTs a template + variables payload to the
n8n webhook, which substitutes {{placeholders}} and sends through Gmail. All calls are
best effort: a mail failure must never break an age check or an API request.
"""
from __future__ import annotations

import httpx

from .config import get_settings


async def send(payload: dict) -> bool:
    """POST a {template, variables} payload to the n8n webhook. Returns True on 2xx.

    No-op (returns False) when the webhook is not configured, so the app stays runnable
    in dev without n8n.
    """
    s = get_settings()
    if not s.n8n_email_webhook_url:
        return False
    headers = {}
    if s.n8n_email_header_secret:
        headers[s.n8n_email_header_name] = s.n8n_email_header_secret
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(s.n8n_email_webhook_url, json=payload, headers=headers)
            resp.raise_for_status()
            return True
    except Exception as e:  # noqa: BLE001 - email is best effort
        print("[email] send failed:", e)
        return False
