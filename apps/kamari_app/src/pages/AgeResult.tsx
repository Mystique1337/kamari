import {
  IonContent, IonPage, IonButton, IonIcon,
} from '@ionic/react';
import {
  checkmarkCircle, shieldCheckmark, alertCircle, refreshCircle, homeOutline, arrowForward,
  chevronDownOutline, chevronUpOutline, sparklesOutline,
} from 'ionicons/icons';
import { useEffect, useState } from 'react';
import { useHistory } from 'react-router-dom';
import { useKamari } from '../lib/state';
import type { Decision } from '../lib/types';

const VISUALS: Record<Decision, { icon: string; label: string; tone: string }> = {
  allow:           { icon: checkmarkCircle, label: 'Verified',       tone: 'var(--kamari-green)' },
  block:           { icon: shieldCheckmark, label: 'Guardian check', tone: '#B83A2E' },
  secondary_check: { icon: alertCircle,     label: 'One more check', tone: '#9a7a1e' },
  recapture:       { icon: refreshCircle,   label: 'Retake photo',   tone: 'var(--kamari-indigo)' },
};

const WHY: Record<string, string> = {
  ALLOW: 'Your estimated age is comfortably above the limit, with good confidence and photo quality.',
  BLOCK_LIKELY_MINOR: 'The model estimated a high chance of being under 18, so access needs a guardian to approve.',
  SECONDARY_CHECK_NEAR_THRESHOLD: 'Your estimate is close to the age limit (the 18 to 21 band), so we ask for one more quick check to be safe.',
  SECONDARY_CHECK_LOW_CONFIDENCE: 'The model was not confident enough on this photo, so we ask for a second check.',
  RECAPTURE_LOW_QUALITY: 'We could not read a clear face, so please retake the photo in good light.',
  RECAPTURE_NO_FACE: 'We did not find a clear single face, so please retake the photo.',
  RECAPTURE_MULTIPLE_FACES: 'We saw more than one face, so please retake with just you in frame.',
};

export default function AgeResult() {
  const { lastResult, reset } = useKamari();
  const history = useHistory();
  const [showWhy, setShowWhy] = useState(false);

  useEffect(() => {
    if (!lastResult) history.replace('/welcome');
  }, [lastResult, history]);
  if (!lastResult) return null;

  const v = VISUALS[lastResult.decision];
  const confidence = Math.round((1 - lastResult.uncertainty) * 100);
  const pUnder = Math.round(lastResult.p_under_18 * 100);
  const quality = Math.round(lastResult.face_quality * 100);
  const ex = lastResult.explanation;
  const byModel = ex?.source === 'model';
  const why = ex?.summary ?? WHY[lastResult.reason_code] ?? 'A second check is needed before continuing.';
  const goHome = () => { reset(); history.replace('/welcome'); };
  const retake = () => { reset(); history.replace('/capture'); };

  return (
    <IonPage>
      <IonContent>
        <div className="kamari-hero kamari-pattern" style={{ padding: '40px 24px 28px', textAlign: 'center' }}>
          <IonIcon icon={v.icon} style={{ fontSize: 72, color: 'var(--kamari-gold)' }} />
          <h1 style={{ color: 'var(--kamari-cream)', margin: '12px 0 0' }}>{v.label}</h1>
          <span className="kamari-badge" style={{ marginTop: 12, background: 'rgba(246,239,226,.16)', color: 'var(--kamari-cream)' }}>
            {lastResult.reason_code.replaceAll('_', ' ').toLowerCase()}
          </span>
        </div>

        <div className="kamari-pad kamari-stack">
          <div className="kamari-card kamari-pad">
            <p style={{ margin: 0, fontSize: '1.05rem', lineHeight: 1.5 }}>{lastResult.message}</p>
            {byModel && (
              <div style={{ marginTop: 10, display: 'flex', alignItems: 'center', gap: 6 }}>
                <IonIcon icon={sparklesOutline} style={{ color: 'var(--kamari-gold)', fontSize: 15 }} />
                <span className="kamari-muted" style={{ fontSize: '.78rem' }}>
                  Explained by Kámárí Gemma{ex?.model_version ? ` (${ex.model_version})` : ''}
                </span>
              </div>
            )}
          </div>

          <div className="kamari-card kamari-pad">
            <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between' }}>
              <span className="kamari-muted" style={{ fontSize: '.9rem' }}>Estimated age</span>
              <span style={{ fontFamily: 'var(--kamari-font-display)', fontSize: '1.8rem' }}>
                {lastResult.estimated_age} <span style={{ fontSize: '.9rem', color: 'var(--kamari-ink-soft)' }}>({lastResult.age_band})</span>
              </span>
            </div>
            <Meter label="Confidence" pct={confidence} tone="var(--kamari-green)" />
            <Meter label="Under-18 probability" pct={pUnder} tone="#B83A2E" />
            <Meter label="Photo quality" pct={quality} tone="var(--kamari-gold)" />
          </div>

          {/* Why this result */}
          <div className="kamari-card kamari-pad">
            <button onClick={() => setShowWhy((s) => !s)} style={{
              all: 'unset', cursor: 'pointer', display: 'flex', width: '100%',
              alignItems: 'center', justifyContent: 'space-between',
            }}>
              <strong>Why this result</strong>
              <IonIcon icon={showWhy ? chevronUpOutline : chevronDownOutline} style={{ color: 'var(--kamari-indigo)' }} />
            </button>
            {showWhy && (
              <div style={{ margin: '10px 0 0' }}>
                <p className="kamari-muted" style={{ margin: 0, fontSize: '.92rem', lineHeight: 1.55 }}>
                  {why}
                  {' '}Decisions are conservative near the age limit and never auto-approve a borderline case.
                </p>
                {ex?.safety_note && (
                  <p className="kamari-muted" style={{ margin: '8px 0 0', fontSize: '.82rem', fontStyle: 'italic' }}>
                    {ex.safety_note}
                  </p>
                )}
                <p className="kamari-muted" style={{ margin: '8px 0 0', fontSize: '.78rem' }}>
                  {byModel
                    ? 'This explanation was written by the Kámárí Gemma model in your language.'
                    : 'Standard explanation (the model layer was unavailable, so an approved template was used).'}
                </p>
              </div>
            )}
            <div style={{ marginTop: 12, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              <span className="kamari-badge">📷 {lastResult.retention.replaceAll('_', ' ')}</span>
              <span className="kamari-badge" style={{ background: 'rgba(33,58,107,.1)', color: 'var(--kamari-indigo)' }}>{lastResult.model_version}</span>
            </div>
          </div>

          {lastResult.decision === 'secondary_check' && (
            <IonButton expand="block" className="kamari-btn" color="secondary" onClick={() => history.push('/secondary')}>
              Continue to secondary check
              <IonIcon slot="end" icon={arrowForward} />
            </IonButton>
          )}
          {lastResult.decision === 'recapture' && (
            <IonButton expand="block" className="kamari-btn" color="secondary" onClick={retake}>
              Retake photo
              <IonIcon slot="end" icon={refreshCircle} />
            </IonButton>
          )}
          <IonButton expand="block" fill="clear" color="primary" onClick={goHome}>
            <IonIcon slot="start" icon={homeOutline} />
            Done
          </IonButton>
          <p className="kamari-muted kamari-center" style={{ fontSize: '.78rem' }}>
            This is an estimate, not a legal age determination.
          </p>
        </div>
      </IonContent>
    </IonPage>
  );
}

function Meter({ label, pct, tone }: { label: string; pct: number; tone: string }) {
  return (
    <div style={{ marginTop: 12 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '.85rem' }}>
        <span className="kamari-muted">{label}</span>
        <span style={{ fontWeight: 600 }}>{pct}%</span>
      </div>
      <div style={{ height: 8, borderRadius: 6, background: 'rgba(120,120,120,.18)', overflow: 'hidden', marginTop: 4 }}>
        <div style={{ width: `${Math.max(0, Math.min(100, pct))}%`, height: '100%', background: tone }} />
      </div>
    </div>
  );
}
