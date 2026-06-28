"""Kamari transactional email templates.

Each builder returns the payload the live n8n workflow expects:
    {"template": {"to","subject","body","isHtml"}, "variables": {...}}
The n8n "Process Template with Variables" node substitutes every {{placeholder}}
in to/subject/body from the variables map, then sends via Gmail.

House style: warm African palette (indigo, gold, terracotta, cream), a kente accent
bar, and plain, respectful copy. No em dashes anywhere.
"""
from __future__ import annotations

INDIGO = "#213A6B"
GOLD = "#E8B84B"
TERRACOTTA = "#C65D3B"
CREAM = "#F6EFE2"
INK = "#14213D"

# A thin kente-inspired band used as a brand accent at the top of every email.
_KENTE = (
    '<div style="height:8px;width:100%;'
    "background:repeating-linear-gradient(90deg,"
    f"{GOLD} 0 22px,{TERRACOTTA} 22px 34px,{INDIGO} 34px 56px,{CREAM} 56px 62px);"
    '"></div>'
)


def _shell(preheader: str, heading: str, inner: str) -> str:
    """Wrap content in the branded, email-safe HTML shell. `inner` may hold {{vars}}."""
    return f"""<!doctype html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:{CREAM};font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:{INK};">
  <span style="display:none;max-height:0;overflow:hidden;opacity:0;">{preheader}</span>
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{CREAM};padding:24px 12px;">
    <tr><td align="center">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 6px 24px rgba(20,33,61,.10);">
        {_KENTE}
        <tr><td style="background:{INDIGO};padding:26px 28px;">
          <div style="color:{GOLD};font-weight:700;letter-spacing:.14em;text-transform:uppercase;font-size:12px;">Kamari</div>
          <div style="color:{CREAM};font-size:22px;font-weight:700;margin-top:6px;">{heading}</div>
        </td></tr>
        <tr><td style="padding:28px;">
          {inner}
        </td></tr>
        <tr><td style="padding:18px 28px;background:{CREAM};">
          <p style="margin:0;font-size:12px;color:#6b6256;line-height:1.6;">
            Kamari is African built, privacy first age verification. Your selfie is processed once and never stored.
            This message was sent to {{{{to}}}}. If you did not expect it, you can ignore it.
          </p>
        </td></tr>
      </table>
      <p style="max-width:560px;margin:14px auto 0;font-size:11px;color:#9a907f;">
        An estimate, not a legal age determination.
      </p>
    </td></tr>
  </table>
</body></html>"""


def _btn(label: str, href: str) -> str:
    return (
        f'<a href="{href}" style="display:inline-block;background:{TERRACOTTA};color:#fff;'
        'text-decoration:none;font-weight:600;padding:12px 22px;border-radius:10px;">'
        f"{label}</a>"
    )


def welcome(*, to: str, name: str, app_url: str) -> dict:
    inner = f"""
      <p style="font-size:16px;margin:0 0 14px;">Welcome, {{{{name}}}}.</p>
      <p style="font-size:15px;line-height:1.6;color:#3b3a36;margin:0 0 18px;">
        Your Kamari account is ready. Kamari gives you a fast, respectful age check tuned for African
        faces and skin tones, with a clear decision and a privacy promise: the photo is never stored.
      </p>
      <p style="margin:0 0 22px;">{_btn("Open Kamari", "{{app_url}}")}</p>
      <p style="font-size:14px;line-height:1.6;color:#3b3a36;margin:0;">
        Next, create an API key from the developer area to start verifying ages from your own app.
      </p>
    """
    return {
        "template": {
            "to": "{{to}}",
            "subject": "Welcome to Kamari",
            "body": _shell("Your Kamari account is ready.", "Welcome to Kamari", inner),
            "isHtml": True,
        },
        "variables": {"to": to, "name": name or "there", "app_url": app_url},
    }


def api_key_created(*, to: str, name: str, key_name: str, api_key: str, app_url: str) -> dict:
    inner = f"""
      <p style="font-size:16px;margin:0 0 14px;">Hello {{{{name}}}},</p>
      <p style="font-size:15px;line-height:1.6;color:#3b3a36;margin:0 0 16px;">
        A new API key named <strong>{{{{key_name}}}}</strong> was created on your Kamari account.
        For your security this is the only time the full key is shown. Store it now in a safe place.
      </p>
      <div style="background:{CREAM};border:1px solid #e7ddca;border-radius:10px;padding:14px 16px;margin:0 0 18px;">
        <div style="font-size:11px;color:#9a907f;text-transform:uppercase;letter-spacing:.1em;margin-bottom:6px;">Your API key</div>
        <code style="font-family:ui-monospace,Menlo,Consolas,monospace;font-size:14px;color:{INDIGO};word-break:break-all;">{{{{api_key}}}}</code>
      </div>
      <p style="margin:0 0 22px;">{_btn("Manage keys", "{{app_url}}")}</p>
      <p style="font-size:13px;line-height:1.6;color:#8a4b3a;margin:0;">
        If you did not create this key, revoke it from the developer area immediately and rotate your password.
      </p>
    """
    return {
        "template": {
            "to": "{{to}}",
            "subject": "Your new Kamari API key",
            "body": _shell("A new API key was created.", "New API key created", inner),
            "isHtml": True,
        },
        "variables": {
            "to": to, "name": name or "there", "key_name": key_name,
            "api_key": api_key, "app_url": app_url,
        },
    }


def api_key_revoked(*, to: str, name: str, key_name: str, app_url: str) -> dict:
    inner = f"""
      <p style="font-size:16px;margin:0 0 14px;">Hello {{{{name}}}},</p>
      <p style="font-size:15px;line-height:1.6;color:#3b3a36;margin:0 0 18px;">
        The API key named <strong>{{{{key_name}}}}</strong> has been revoked and can no longer be used.
        Any app still using it will start receiving authentication errors.
      </p>
      <p style="margin:0 0 18px;">{_btn("Create a new key", "{{app_url}}")}</p>
      <p style="font-size:13px;line-height:1.6;color:#3b3a36;margin:0;">
        If this was not you, please secure your account right away.
      </p>
    """
    return {
        "template": {
            "to": "{{to}}",
            "subject": "A Kamari API key was revoked",
            "body": _shell("An API key was revoked.", "API key revoked", inner),
            "isHtml": True,
        },
        "variables": {"to": to, "name": name or "there", "key_name": key_name, "app_url": app_url},
    }


def guardian_consent(*, to: str, guardian_name: str, consent_url: str, code: str, app_name: str) -> dict:
    inner = f"""
      <p style="font-size:16px;margin:0 0 14px;">Hello {{{{guardian_name}}}},</p>
      <p style="font-size:15px;line-height:1.6;color:#3b3a36;margin:0 0 16px;">
        Someone in your care is trying to access <strong>{{{{app_name}}}}</strong>, which requires an adult age check.
        Kamari estimated that they may be under age, so we are asking a guardian to review and decide.
      </p>
      <div style="background:{CREAM};border:1px solid #e7ddca;border-radius:10px;padding:16px;margin:0 0 18px;text-align:center;">
        <div style="font-size:11px;color:#9a907f;text-transform:uppercase;letter-spacing:.1em;margin-bottom:8px;">Your consent code</div>
        <div style="font-family:ui-monospace,Menlo,Consolas,monospace;font-size:30px;letter-spacing:.22em;color:{INDIGO};font-weight:700;">{{{{code}}}}</div>
      </div>
      <p style="margin:0 0 18px;">{_btn("Review and respond", "{{consent_url}}")}</p>
      <p style="font-size:13px;line-height:1.6;color:#3b3a36;margin:0;">
        If you do not recognise this request, you can safely ignore this email and no access will be granted.
      </p>
    """
    return {
        "template": {
            "to": "{{to}}",
            "subject": "A guardian age check is needed",
            "body": _shell("A guardian age check is needed.", "Guardian age check", inner),
            "isHtml": True,
        },
        "variables": {
            "to": to, "guardian_name": guardian_name or "there",
            "consent_url": consent_url, "code": code, "app_name": app_name or "an app",
        },
    }
