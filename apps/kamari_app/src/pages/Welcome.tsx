import { IonContent, IonPage, IonButton, IonIcon } from '@ionic/react';
import {
  arrowForward, eyeOffOutline, globeOutline, flashOutline, shieldCheckmarkOutline,
  sparklesOutline, logoGithub, copyOutline, checkmarkOutline, logoAndroid,
} from 'ionicons/icons';
import { useState, type CSSProperties } from 'react';
import { useHistory } from 'react-router-dom';
import KamariMark from '../components/KamariMark';
import { apiBase } from '../lib/api';
import { DEMO_LIST } from '../lib/demos';

const BASE = apiBase || 'https://kamari-api.shinzii.tech';

const STATS = [
  { num: '480,828', lbl: 'face images, cleaned and curated' },
  { num: '6.03 yrs', lbl: 'mean absolute age error' },
  { num: '9', lbl: 'languages explained' },
  { num: '0', lbl: 'images stored, ever' },
];

const FEATURES = [
  { icon: eyeOffOutline, title: 'Privacy first', body: 'The selfie is processed once and deleted. We log the decision, never the image.' },
  { icon: globeOutline, title: 'Built for Africa', body: 'Trained and benchmarked across African faces and skin tones, with fairness slices.' },
  { icon: flashOutline, title: 'Fast and multilingual', body: 'A decision in a moment, explained in the user\'s language by a fine-tuned Gemma model.' },
  { icon: shieldCheckmarkOutline, title: 'Safe by design', body: 'Conservative near the limit. Liveness and a guardian flow back up the model.' },
];

const MAE_BY_SKIN: [string, string][] = [
  ['Very light', '5.46'], ['Light', '5.72'], ['Intermediate', '5.50'],
  ['Tan', '5.99'], ['Brown', '6.23'], ['Dark', '6.58'],
];

const SNIPPETS: Record<string, string> = {
  curl: `curl -X POST ${BASE}/v1/age/estimate \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -F image=@selfie.jpg -F language=en -F country=NG`,
  javascript: `const form = new FormData();
form.append("image", file);            // a File/Blob
form.append("language", "en");
const res = await fetch("${BASE}/v1/age/estimate", {
  method: "POST",
  headers: { Authorization: "Bearer YOUR_API_KEY" },
  body: form,
});
const { decision, estimated_age } = await res.json();`,
  python: `import requests
with open("selfie.jpg", "rb") as image:
    r = requests.post(
        "${BASE}/v1/age/estimate",
        headers={"Authorization": "Bearer YOUR_API_KEY"},
        files={"image": image},
        data={"language": "en", "country": "NG"},
    )
print(r.json()["decision"], r.json()["estimated_age"])`,
};

const PLANS = [
  { name: 'Free', price: '$0', items: ['1,000 checks / mo', '10 req / min', 'Community support'] },
  { name: 'Growth', price: '$29', items: ['50,000 checks / mo', '60 req / min', 'Email support'] },
  { name: 'Scale', price: '$199', items: ['500,000 checks / mo', '300 req / min', 'Fairness reports'] },
];

const HF = 'https://huggingface.co/Shinzmann';
// Always-latest Android build, published by CI on every push to main.
const APK_URL = 'https://github.com/Mystique1337/kamari/releases/latest/download/kamari.apk';
const ARTIFACTS = [
  { tag: 'Model', title: 'CNN age model', desc: 'EfficientNetV2-S. MAE 6.03, with the MPTR safety metric.', href: `${HF}/cnn-age-v0` },
  { tag: 'Model', title: 'Gemma explanation LoRA', desc: 'Strict-JSON, multilingual decision messages.', href: `${HF}/gemma-explain-lora-v0` },
  { tag: 'Benchmark', title: 'Kámárí-Safe Open v0', desc: 'Fairness slices and the 13 to 21 boundary.', href: `${HF}/kamari-safe-open-v0` },
  { tag: 'Dataset', title: 'Dataset registry', desc: 'Provenance, licences, and the data manifest.', href: `${HF}/dataset-registry-v0` },
];

const TEAM = [
  { name: 'Emmanuel Ashinze', role: 'Engineering and API' },
  { name: 'Taiwo Olatunji', role: 'Machine learning and data' },
  { name: 'Kolade Boluwatife', role: 'Product and frontend' },
];

function scrollTo(id: string) {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

export default function Welcome() {
  const history = useHistory();
  const [lang, setLang] = useState<'curl' | 'javascript' | 'python'>('curl');
  const [copied, setCopied] = useState(false);
  const copy = () => { navigator.clipboard?.writeText(SNIPPETS[lang]); setCopied(true); setTimeout(() => setCopied(false), 1500); };

  return (
    <IonPage>
      <IonContent fullscreen className="mkt">
        {/* Nav */}
        <nav className="mkt-nav">
          <span className="brand">Kámárí</span>
          <button className="link hide-sm" onClick={() => scrollTo('how')}>How it works</button>
          <button className="link hide-sm" onClick={() => history.push('/demos')}>Demos</button>
          <button className="link hide-sm" onClick={() => scrollTo('data')}>Benchmarks</button>
          <button className="link hide-sm" onClick={() => history.push('/docs')}>Docs</button>
          <button className="link hide-sm" onClick={() => history.push('/pricing')}>Pricing</button>
          <button className="link hide-sm" onClick={() => scrollTo('about')}>About</button>
          <span className="spacer" />
          <button className="link" onClick={() => history.push('/login')}>Developers</button>
          <IonButton size="small" className="kamari-btn" color="secondary" onClick={() => history.push('/consent')}>Try it out</IonButton>
        </nav>

        {/* Hero (signature Adire indigo + Adinkra pattern) */}
        <section className="kamari-hero kamari-pattern">
          <div className="mkt-wrap mkt-hero-indigo" style={{ textAlign: 'center' }}>
            <div style={{ display: 'flex', justifyContent: 'center' }}><KamariMark size={84} tone="gold" /></div>
            <p className="kamari-eyebrow">African-built age verification</p>
            <h1>Prove age with a selfie.<br />Privacy kept, not your photo.</h1>
            <p className="sub">
              Kámárí estimates age from a single selfie, returns a calibrated decision, and explains
              it in the user's language. Tuned for African faces. Open source, with a managed API.
            </p>
            <div className="mkt-cta">
              <IonButton className="kamari-btn" color="secondary" onClick={() => history.push('/consent')}>
                Try it out <IonIcon slot="end" icon={arrowForward} />
              </IonButton>
              <IonButton
                fill="outline"
                onClick={() => history.push('/docs')}
                style={{ '--color': 'var(--kamari-cream)', '--border-color': 'rgba(246,239,226,.55)' } as CSSProperties}
              >
                Read the docs
              </IonButton>
              <IonButton
                fill="outline"
                href={APK_URL}
                rel="noreferrer"
                style={{ '--color': 'var(--kamari-cream)', '--border-color': 'rgba(246,239,226,.55)' } as CSSProperties}
              >
                <IonIcon slot="start" icon={logoAndroid} /> Get the Android app
              </IonButton>
            </div>
            <div className="mkt-herostats">
              {STATS.map((s) => (
                <div key={s.lbl} className="mkt-herostat">
                  <div className="n">{s.num}</div>
                  <div className="l">{s.lbl}</div>
                </div>
              ))}
            </div>
          </div>
          <div className="mkt-wrap" style={{ paddingBottom: 26 }}><div className="kamari-kente" /></div>
        </section>

        {/* How it works */}
        <section id="how" className="mkt-section">
          <div className="mkt-wrap">
            <h2 className="mkt-h2">How it works</h2>
            <p className="mkt-lead">A small CNN makes the age signal, a policy engine decides, and a fine-tuned Gemma model writes the message. The image never leaves the moment.</p>
            <div className="mkt-grid-3" style={{ marginTop: 22 }}>
              {[['1', 'Capture', 'The user takes a selfie. We detect and crop the face on the fly.'],
                ['2', 'Estimate', 'The model returns an age, an under-18 probability, and an uncertainty.'],
                ['3', 'Decide', 'A conservative policy returns allow, secondary check, block, or recapture, with a clear message.']].map(([n, t, d]) => (
                <div key={n} className="kamari-card kamari-pad">
                  <div style={{ width: 34, height: 34, borderRadius: '50%', background: 'var(--kamari-gold)', color: 'var(--kamari-indigo-deep)', display: 'grid', placeItems: 'center', fontWeight: 700 }}>{n}</div>
                  <h3 style={{ margin: '10px 0 4px' }}>{t}</h3>
                  <p className="kamari-muted" style={{ margin: 0, fontSize: '.92rem' }}>{d}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* See it in action: demo integrations */}
        <section id="demos" className="mkt-section">
          <div className="mkt-wrap">
            <h2 className="mkt-h2">See it in action</h2>
            <p className="mkt-lead">
              Three mock partner apps that call the Kamari API and allow or restrict entry on the
              decision. Try one with a selfie or an uploaded photo.
            </p>
            <div className="mkt-grid-3" style={{ marginTop: 22 }}>
              {DEMO_LIST.map((d) => (
                <button key={d.kind} onClick={() => history.push(`/demo/${d.kind}`)}
                  className="kamari-card kamari-pad" style={{ textAlign: 'left', cursor: 'pointer', border: 'none', width: '100%' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <span style={{ width: 40, height: 40, borderRadius: 10, background: d.accent, display: 'grid', placeItems: 'center', flexShrink: 0 }}>
                      <IonIcon icon={d.icon} style={{ color: '#fff', fontSize: 22 }} />
                    </span>
                    <div>
                      <strong>{d.name}</strong>
                      <p className="kamari-muted" style={{ margin: 0, fontSize: '.85rem' }}>{d.tagline}</p>
                    </div>
                  </div>
                  <span style={{ color: 'var(--kamari-indigo)', fontWeight: 600, fontSize: '.85rem', display: 'inline-block', marginTop: 12 }}>Open demo</span>
                </button>
              ))}
            </div>
          </div>
        </section>

        {/* Features */}
        <section className="mkt-section alt">
          <div className="mkt-wrap">
            <h2 className="mkt-h2">Why Kámárí</h2>
            <div className="mkt-grid" style={{ marginTop: 22 }}>
              {FEATURES.map((f) => (
                <div key={f.title} className="kamari-card kamari-pad">
                  <IonIcon icon={f.icon} style={{ fontSize: 26, color: 'var(--kamari-indigo)' }} />
                  <h3 style={{ margin: '8px 0 4px' }}>{f.title}</h3>
                  <p className="kamari-muted" style={{ margin: 0, fontSize: '.92rem' }}>{f.body}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Data & benchmarks */}
        <section id="data" className="mkt-section">
          <div className="mkt-wrap">
            <h2 className="mkt-h2">Data, benchmarks, and evaluation</h2>
            <p className="mkt-lead">
              Built from open, license-checked face datasets with an auto label-quality gate, MTCNN
              face crops, skin-tone banding, and a leakage-free split. We report fairness and the
              critical 13 to 21 boundary, not just an average.
            </p>

            <div className="mkt-grid" style={{ marginTop: 22 }}>
              {[['825,129', 'images gathered'], ['480,828', 'kept after cleaning'],
                ['24,753', 'exact-age training rows'], ['10,182', 'African-signal rows'],
                ['3,139', 'in the 13 to 21 boundary'], ['8,322', 'held-out benchmark']].map(([n, l]) => (
                <div key={l} className="kamari-card mkt-stat"><div className="num">{n}</div><div className="lbl">{l}</div></div>
              ))}
            </div>

            <div className="mkt-grid-3" style={{ marginTop: 24, alignItems: 'start' }}>
              <div className="kamari-card kamari-pad">
                <h3 style={{ marginTop: 0 }}>Accuracy</h3>
                <table className="mkt-table">
                  <tbody>
                    <tr><td>MAE</td><td><strong>6.03 yrs</strong></td></tr>
                    <tr><td>MPTR@18</td><td>0.317</td></tr>
                    <tr><td>MPTR@18, dark + brown</td><td>0.383</td></tr>
                    <tr><td>Adults wrongly blocked</td><td>1%</td></tr>
                    <tr><td>Model inference</td><td>~14 ms</td></tr>
                  </tbody>
                </table>
              </div>
              <div className="kamari-card kamari-pad">
                <h3 style={{ marginTop: 0 }}>MAE by skin band</h3>
                <table className="mkt-table">
                  <tbody>{MAE_BY_SKIN.map(([b, v]) => (<tr key={b}><td>{b}</td><td>{v} yrs</td></tr>))}</tbody>
                </table>
              </div>
              <div className="kamari-card kamari-pad">
                <h3 style={{ marginTop: 0 }}>How we evaluate</h3>
                <p className="kamari-muted" style={{ fontSize: '.92rem', lineHeight: 1.6 }}>
                  The headline metric is <strong>Minor-Pass-Through Rate</strong>, the share of true
                  minors passed as adults, reported overall, at 21, and for dark and brown skin. The
                  CNN is a signal, not a standalone gate: the policy engine, liveness, and guardian
                  flow provide the safety margin.
                </p>
                <a href="https://github.com/Mystique1337/kamari/blob/main/docs/methodology.md" target="_blank" rel="noreferrer" style={{ color: 'var(--kamari-indigo)', fontWeight: 600, fontSize: '.9rem' }}>Read the methodology</a>
              </div>
            </div>
          </div>
        </section>

        {/* Code */}
        <section className="mkt-section alt">
          <div className="mkt-wrap">
            <h2 className="mkt-h2">One request to verify age</h2>
            <p className="mkt-lead">Create a key in the developer area, then call the API from anywhere.</p>
            <div style={{ marginTop: 18 }}>
              <div className="mkt-tabs">
                {(['curl', 'javascript', 'python'] as const).map((l) => (
                  <button key={l} className={`mkt-tab ${lang === l ? 'active' : ''}`} onClick={() => setLang(l)}>{l}</button>
                ))}
                <span style={{ flex: 1 }} />
                <button className="mkt-tab" onClick={copy}><IonIcon icon={copied ? checkmarkOutline : copyOutline} /> {copied ? 'Copied' : 'Copy'}</button>
              </div>
              <pre className="mkt-code"><code>{SNIPPETS[lang]}</code></pre>
            </div>
          </div>
        </section>

        {/* Built in the open: deliverables + artifacts */}
        <section id="artifacts" className="mkt-section">
          <div className="mkt-wrap">
            <h2 className="mkt-h2">Built in the open</h2>
            <p className="mkt-lead">
              Four deliverables: a dataset and benchmark, a CNN age model, a Gemma explanation model,
              and the API and apps. The code is Apache-2.0 on GitHub; the models, benchmark, and data
              registry live on Hugging Face.
            </p>
            <div className="mkt-grid" style={{ marginTop: 22 }}>
              {ARTIFACTS.map((a) => (
                <a key={a.title} href={a.href} target="_blank" rel="noreferrer"
                  className="kamari-card kamari-pad" style={{ textDecoration: 'none', color: 'inherit', display: 'block' }}>
                  <span className="kamari-badge" style={{ background: 'rgba(33,58,107,.1)', color: 'var(--kamari-indigo)' }}>{a.tag}</span>
                  <h3 style={{ margin: '10px 0 4px' }}>{a.title}</h3>
                  <p className="kamari-muted" style={{ margin: 0, fontSize: '.9rem' }}>{a.desc}</p>
                  <span style={{ color: 'var(--kamari-indigo)', fontWeight: 600, fontSize: '.85rem', display: 'inline-block', marginTop: 10 }}>
                    View on Hugging Face
                  </span>
                </a>
              ))}
            </div>
            <div style={{ marginTop: 18, display: 'flex', gap: 12, flexWrap: 'wrap' }}>
              <IonButton fill="outline" href="https://github.com/Mystique1337/kamari" target="_blank" rel="noreferrer">
                <IonIcon slot="start" icon={logoGithub} /> Code on GitHub
              </IonButton>
              <IonButton fill="clear" href="https://github.com/Mystique1337/kamari/blob/main/docs/methodology.md" target="_blank" rel="noreferrer">
                Read the methodology
              </IonButton>
            </div>
          </div>
        </section>

        {/* Pricing teaser */}
        <section className="mkt-section">
          <div className="mkt-wrap">
            <h2 className="mkt-h2">Pricing</h2>
            <p className="mkt-lead">Pay for the volume you verify. Self-host it free under Apache 2.0, or use the managed API.</p>
            <div className="mkt-grid-3" style={{ marginTop: 22 }}>
              {PLANS.map((p) => (
                <div key={p.name} className="kamari-card kamari-pad">
                  <strong style={{ fontSize: '1.1rem' }}>{p.name}</strong>
                  <div style={{ fontFamily: 'var(--kamari-font-display)', fontSize: '2rem', margin: '6px 0' }}>{p.price}{p.price !== '$0' && <span style={{ fontSize: '.85rem', color: 'var(--kamari-ink-soft)' }}> /mo</span>}</div>
                  {p.items.map((it) => (
                    <div key={it} style={{ display: 'flex', gap: 8, alignItems: 'center', fontSize: '.9rem', margin: '4px 0' }}>
                      <IonIcon icon={checkmarkOutline} style={{ color: 'var(--kamari-green)' }} /> {it}
                    </div>
                  ))}
                </div>
              ))}
            </div>
            <div style={{ marginTop: 16 }}>
              <IonButton fill="outline" color="primary" onClick={() => history.push('/pricing')}>
                <IonIcon slot="start" icon={sparklesOutline} /> See full pricing
              </IonButton>
            </div>
          </div>
        </section>

        {/* About */}
        <section id="about" className="mkt-section alt">
          <div className="mkt-wrap">
            <h2 className="mkt-h2">About us</h2>
            <p className="mkt-lead">
              Kámárí is a small African team building age assurance that respects people. Age checks
              should not mean surrendering your face to a database. We keep the decision, never the
              image, and we test for fairness across skin tones because most age models are not built
              or measured here.
            </p>
            <div className="mkt-grid-3" style={{ marginTop: 22 }}>
              {TEAM.map((m) => (
                <div key={m.name} className="kamari-card kamari-pad">
                  <strong>{m.name}</strong>
                  <p className="kamari-muted" style={{ margin: '4px 0 0', fontSize: '.9rem' }}>{m.role}</p>
                </div>
              ))}
            </div>
            <p className="mkt-lead" style={{ marginTop: 16 }}>Contact: kamari.support@gmail.com</p>
          </div>
        </section>

        {/* Footer */}
        <footer className="mkt-footer">
          <div className="mkt-wrap" style={{ display: 'flex', gap: 16, flexWrap: 'wrap', alignItems: 'center' }}>
            <span className="brand" style={{ fontFamily: 'var(--kamari-font-display)', fontWeight: 700 }}>Kámárí</span>
            <span className="spacer" style={{ flex: 1 }} />
            <a href="https://github.com/Mystique1337/kamari" target="_blank" rel="noreferrer"><IonIcon icon={logoGithub} /> GitHub</a>
            <a href={HF} target="_blank" rel="noreferrer">Hugging Face</a>
            <a href={APK_URL} rel="noreferrer"><IonIcon icon={logoAndroid} /> Android app</a>
            <button className="link" onClick={() => history.push('/docs')} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'inherit' }}>Docs</button>
            <button className="link" onClick={() => history.push('/pricing')} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'inherit' }}>Pricing</button>
            <button className="link" onClick={() => history.push('/privacy')} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'inherit' }}>Privacy</button>
            <button className="link" onClick={() => history.push('/terms')} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'inherit' }}>Terms</button>
            <span>Apache-2.0. An estimate, not a legal determination.</span>
          </div>
        </footer>
      </IonContent>
    </IonPage>
  );
}
