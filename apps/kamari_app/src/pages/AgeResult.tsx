import {
  IonContent, IonPage, IonButton, IonIcon,
} from '@ionic/react';
import {
  checkmarkCircle, shieldCheckmark, alertCircle, refreshCircle, homeOutline, arrowForward,
} from 'ionicons/icons';
import { useEffect } from 'react';
import { useHistory } from 'react-router-dom';
import { useKamari } from '../lib/state';
import type { Decision } from '../lib/types';

const VISUALS: Record<Decision, { icon: string; chip: string; label: string; tone: string }> = {
  allow:           { icon: checkmarkCircle, chip: 'decision-allow',     label: 'Verified',        tone: 'var(--kamari-green)' },
  block:           { icon: shieldCheckmark, chip: 'decision-block',     label: 'Guardian check',  tone: '#B83A2E' },
  secondary_check: { icon: alertCircle,     chip: 'decision-check',     label: 'One more check',  tone: '#9a7a1e' },
  recapture:       { icon: refreshCircle,   chip: 'decision-recapture', label: 'Retake photo',    tone: 'var(--kamari-indigo)' },
};

export default function AgeResult() {
  const { lastResult, reset } = useKamari();
  const history = useHistory();

  useEffect(() => {
    if (!lastResult) history.replace('/welcome');
  }, [lastResult, history]);
  if (!lastResult) return null;

  const v = VISUALS[lastResult.decision];
  const goHome = () => { reset(); history.replace('/welcome'); };
  const retake = () => { reset(); history.replace('/capture'); };

  return (
    <IonPage>
      <IonContent className="kamari-bg">
        <div className="kamari-hero kamari-pattern" style={{ padding: '40px 24px 28px', textAlign: 'center' }}>
          <IonIcon icon={v.icon} style={{ fontSize: 72, color: 'var(--kamari-gold)' }} />
          <h1 style={{ color: 'var(--kamari-cream)', margin: '12px 0 0' }}>{v.label}</h1>
          <span className={`kamari-badge`} style={{ marginTop: 12, background: 'rgba(246,239,226,.16)', color: 'var(--kamari-cream)' }}>
            {lastResult.reason_code.replaceAll('_', ' ').toLowerCase()}
          </span>
        </div>

        <div className="kamari-pad kamari-stack">
          <div className="kamari-card kamari-pad">
            <p style={{ margin: 0, fontSize: '1.05rem', lineHeight: 1.5 }}>{lastResult.message}</p>
          </div>

          <div className="kamari-card kamari-pad">
            <p className="kamari-eyebrow" style={{ color: 'var(--kamari-terracotta)' }}>Estimate details</p>
            <Row k="Estimated age" val={`${lastResult.estimated_age} (${lastResult.age_band})`} />
            <Row k="Under-18 probability" val={`${Math.round(lastResult.p_under_18 * 100)}%`} />
            <Row k="Confidence" val={`${Math.round((1 - lastResult.uncertainty) * 100)}%`} />
            <Row k="Photo quality" val={`${Math.round(lastResult.face_quality * 100)}%`} />
            <Row k="Model" val={lastResult.model_version} />
            <Row k="Request ID" val={lastResult.request_id} mono />
            <div style={{ marginTop: 12 }}>
              <span className="kamari-badge">📷 {lastResult.retention.replaceAll('_', ' ')}</span>
            </div>
          </div>

          {lastResult.decision === 'secondary_check' && (
            <IonButton expand="block" className="kamari-btn" color="secondary">
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

function Row({ k, val, mono }: { k: string; val: string; mono?: boolean }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, padding: '7px 0', borderBottom: '1px solid rgba(33,58,107,.07)' }}>
      <span className="kamari-muted" style={{ fontSize: '.9rem' }}>{k}</span>
      <span style={{ fontWeight: 600, fontSize: '.9rem', fontFamily: mono ? 'monospace' : 'inherit' }}>{val}</span>
    </div>
  );
}
