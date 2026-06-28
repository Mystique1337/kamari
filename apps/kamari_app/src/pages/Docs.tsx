import {
  IonContent, IonPage, IonHeader, IonToolbar, IonTitle, IonButtons, IonBackButton,
  IonSegment, IonSegmentButton, IonLabel, IonIcon,
} from '@ionic/react';
import { copyOutline, checkmarkOutline } from 'ionicons/icons';
import { useState } from 'react';
import { apiBase } from '../lib/api';

const BASE = apiBase || 'https://kamari-api.shinzii.tech';

function Code({ code }: { code: string }) {
  const [copied, setCopied] = useState(false);
  const copy = () => {
    navigator.clipboard?.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };
  return (
    <div style={{ position: 'relative', margin: '10px 0' }}>
      <pre style={{
        background: '#0d1830', color: '#e7e0d0', padding: '14px 16px', borderRadius: 12,
        overflowX: 'auto', fontSize: '.8rem', lineHeight: 1.5, margin: 0,
      }}><code>{code}</code></pre>
      <button onClick={copy} aria-label="Copy" style={{
        position: 'absolute', top: 8, right: 8, background: 'rgba(246,239,226,.14)',
        border: 'none', borderRadius: 8, color: '#f6efe2', padding: '4px 8px', cursor: 'pointer',
      }}>
        <IonIcon icon={copied ? checkmarkOutline : copyOutline} />
      </button>
    </div>
  );
}

const SNIPPETS: Record<string, string> = {
  curl: `curl -X POST ${BASE}/v1/age/estimate \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -F image=@selfie.jpg \\
  -F language=en \\
  -F country=NG`,
  javascript: `const form = new FormData();
form.append("image", fileInput.files[0]); // a File/Blob
form.append("language", "en");
form.append("country", "NG");

const res = await fetch("${BASE}/v1/age/estimate", {
  method: "POST",
  headers: { Authorization: "Bearer YOUR_API_KEY" },
  body: form,
});
const result = await res.json();
console.log(result.decision, result.estimated_age);`,
  python: `import requests

with open("selfie.jpg", "rb") as image:
    res = requests.post(
        "${BASE}/v1/age/estimate",
        headers={"Authorization": "Bearer YOUR_API_KEY"},
        files={"image": image},
        data={"language": "en", "country": "NG"},
    )

result = res.json()
print(result["decision"], result["estimated_age"])`,
};

const RESPONSE = `{
  "request_id": "req_8f3c12ab90de",
  "model_version": "cnn_v0.1.0",
  "estimated_age": 24.1,
  "age_band": "21-25",
  "p_under_18": 0.002,
  "uncertainty": 0.27,
  "face_quality": 1.0,
  "decision": "allow",
  "reason_code": "ALLOW",
  "message": "You are verified. Welcome in.",
  "retention": "image_not_stored"
}`;

const DECISIONS = [
  ['allow', 'Age requirement met. Let the user through.'],
  ['secondary_check', 'Borderline (near 18 to 21) or low confidence. Run a second check.'],
  ['block', 'Likely under age. Hand off to the guardian flow.'],
  ['recapture', 'No clear face or poor quality. Ask for a new photo.'],
];

export default function Docs() {
  const [lang, setLang] = useState<'curl' | 'javascript' | 'python'>('curl');

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonButtons slot="start"><IonBackButton defaultHref="/welcome" /></IonButtons>
          <IonTitle>Developer docs</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent className="kamari-bg kamari-pad">
        <p className="kamari-eyebrow" style={{ color: 'var(--kamari-terracotta)' }}>Kamari API</p>
        <h2 style={{ marginTop: 6 }}>Verify age in one request</h2>
        <p className="kamari-muted">
          Kamari is a privacy-first age check tuned for African faces. Send a selfie, get a decision
          and a clear, multilingual message. The image is processed once and never stored.
        </p>

        <h3 style={{ marginTop: 22 }}>Base URL</h3>
        <Code code={BASE} />

        <h3 style={{ marginTop: 18 }}>Authentication</h3>
        <p className="kamari-muted">
          Create an API key in the developer area and send it as a bearer token. Keys are scoped to
          your organization and are rate limited by your plan.
        </p>
        <Code code={`Authorization: Bearer YOUR_API_KEY`} />

        <h3 style={{ marginTop: 18 }}>Quickstart</h3>
        <p className="kamari-muted">Estimate age from a selfie. Multipart form fields: <code>image</code> (required), <code>language</code>, <code>country</code>.</p>
        <IonSegment value={lang} onIonChange={(e) => setLang((e.detail.value as typeof lang) ?? 'curl')}>
          <IonSegmentButton value="curl"><IonLabel>curl</IonLabel></IonSegmentButton>
          <IonSegmentButton value="javascript"><IonLabel>JavaScript</IonLabel></IonSegmentButton>
          <IonSegmentButton value="python"><IonLabel>Python</IonLabel></IonSegmentButton>
        </IonSegment>
        <Code code={SNIPPETS[lang]} />

        <h3 style={{ marginTop: 18 }}>Response</h3>
        <Code code={RESPONSE} />

        <h3 style={{ marginTop: 18 }}>Decisions</h3>
        <div className="kamari-card" style={{ padding: 4 }}>
          {DECISIONS.map(([k, v]) => (
            <div key={k} style={{ padding: '10px 12px', borderBottom: '1px solid rgba(33,58,107,.08)' }}>
              <code style={{ color: 'var(--kamari-indigo)', fontWeight: 600 }}>{k}</code>
              <div className="kamari-muted" style={{ fontSize: '.85rem', marginTop: 2 }}>{v}</div>
            </div>
          ))}
        </div>

        <h3 style={{ marginTop: 18 }}>Languages</h3>
        <p className="kamari-muted">
          Pass <code>language</code> to get the message in that language. Supported: English (en),
          Nigerian Pidgin (pcm), French (fr), Swahili (sw), Yoruba (yo), Hausa (ha), Igbo (ig),
          Zulu (zu), Amharic (am).
        </p>

        <h3 style={{ marginTop: 18 }}>Rate limits</h3>
        <p className="kamari-muted">
          Each plan sets requests per minute and a monthly quota. Exceeding either returns
          <code> 429 Too Many Requests</code>. See your plan on the Pricing page.
        </p>

        <h3 style={{ marginTop: 18 }}>Errors</h3>
        <div className="kamari-card" style={{ padding: 4 }}>
          {[['400', 'Malformed request or unsupported image.'],
            ['401', 'Missing or invalid API key.'],
            ['429', 'Rate limit or monthly quota reached. Upgrade your plan.'],
            ['500', 'Unexpected error. Safe to retry with backoff.']].map(([c, d]) => (
            <div key={c} style={{ padding: '10px 12px', borderBottom: '1px solid rgba(33,58,107,.08)' }}>
              <code style={{ color: '#B83A2E', fontWeight: 600 }}>{c}</code>
              <span className="kamari-muted" style={{ fontSize: '.85rem', marginLeft: 8 }}>{d}</span>
            </div>
          ))}
        </div>

        <div className="kamari-kente" style={{ margin: '22px 0 14px' }} />
        <p className="kamari-muted kamari-center" style={{ fontSize: '.8rem' }}>
          Kamari is open source under Apache 2.0. Self-host it or use the managed API.
        </p>
      </IonContent>
    </IonPage>
  );
}
