import {
  IonContent, IonPage, IonHeader, IonToolbar, IonTitle, IonButtons, IonBackButton,
  IonIcon, IonButton,
} from '@ionic/react';
import { lockClosedOutline, checkmarkCircle, closeCircle, refreshOutline } from 'ionicons/icons';
import { useState, type CSSProperties } from 'react';
import { useParams, useHistory, Redirect } from 'react-router-dom';
import AgeGate from '../components/AgeGate';
import { DEMOS } from '../lib/demos';
import type { AgeEstimateResponse } from '../lib/types';

export default function Demo() {
  const { kind } = useParams<{ kind: string }>();
  const history = useHistory();
  const demo = DEMOS[kind];
  const [result, setResult] = useState<AgeEstimateResponse | null>(null);

  if (!demo) return <Redirect to="/demos" />;
  const allowed = result?.decision === 'allow';
  const reset = () => setResult(null);

  const hero = (
    <div style={{ position: 'relative', borderRadius: 'var(--kamari-radius)', overflow: 'hidden', background: demo.accent, marginBottom: 18 }}>
      <img src={demo.hero} alt="" style={{ width: '100%', height: 160, objectFit: 'cover', display: 'block', opacity: 0.92 }} />
      <div style={{ position: 'absolute', inset: 0, background: `linear-gradient(180deg, transparent 30%, ${demo.accent}e6)` }} />
      <div style={{ position: 'absolute', left: 16, bottom: 14, color: '#fff', display: 'flex', alignItems: 'center', gap: 10 }}>
        <IonIcon icon={demo.icon} style={{ fontSize: 28 }} />
        <div>
          <strong style={{ fontSize: '1.3rem' }}>{demo.name}</strong>
          <div style={{ opacity: 0.9, fontSize: '.85rem' }}>{demo.tagline}</div>
        </div>
      </div>
    </div>
  );

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar style={{ '--background': demo.accent, '--color': '#fff' } as CSSProperties}>
          <IonButtons slot="start"><IonBackButton defaultHref="/demos" /></IonButtons>
          <IonTitle>{demo.name}</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent className="kamari-pad">
        {hero}

        {!result && (
          <div className="kamari-card kamari-pad kamari-center">
            <IonIcon icon={lockClosedOutline} style={{ fontSize: 32, color: demo.accent }} />
            <h3 style={{ margin: '8px 0 4px' }}>Age check required</h3>
            <p className="kamari-muted" style={{ marginTop: 0 }}>{demo.gate}</p>
            <div style={{ marginTop: 12 }}><AgeGate onResult={setResult} /></div>
          </div>
        )}

        {result && allowed && (
          <>
            <div className="kamari-card kamari-pad" style={{ display: 'flex', gap: 12, alignItems: 'center', marginBottom: 14 }}>
              <IonIcon icon={checkmarkCircle} style={{ fontSize: 30, color: 'var(--kamari-green)', flexShrink: 0 }} />
              <div>
                <strong>Welcome to {demo.name}</strong>
                <div className="kamari-muted" style={{ fontSize: '.85rem' }}>{demo.allowed} Estimated age {result.estimated_age}.</div>
              </div>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))', gap: 12 }}>
              {demo.items.map((it) => (
                <div key={it.title} className="kamari-card" style={{ overflow: 'hidden' }}>
                  <div style={{ height: 96, background: demo.accent }}>
                    <img src={it.img} alt="" loading="lazy" style={{ width: '100%', height: 96, objectFit: 'cover', display: 'block' }} />
                  </div>
                  <div style={{ padding: '10px 12px' }}>
                    <strong style={{ fontSize: '.9rem' }}>{it.title}</strong>
                    <div className="kamari-muted" style={{ fontSize: '.8rem', marginTop: 2 }}>{it.meta}</div>
                  </div>
                </div>
              ))}
            </div>
            <IonButton expand="block" fill="clear" style={{ marginTop: 14 }} onClick={reset}>
              <IonIcon slot="start" icon={refreshOutline} /> Run the check again
            </IonButton>
          </>
        )}

        {result && !allowed && (
          <div className="kamari-card kamari-pad kamari-center">
            <IonIcon icon={closeCircle} style={{ fontSize: 52, color: '#B83A2E' }} />
            <h3 style={{ margin: '8px 0 4px' }}>{result.decision === 'block' ? 'Entry restricted' : 'One more step'}</h3>
            <p className="kamari-muted">{result.message}</p>
            <p style={{ fontSize: '.8rem' }}>Decision: {result.decision.replaceAll('_', ' ')}.</p>
            <IonButton className="kamari-btn" color="secondary" onClick={reset}>
              <IonIcon slot="start" icon={refreshOutline} /> Try again
            </IonButton>
          </div>
        )}

        <IonButton expand="block" fill="clear" style={{ marginTop: 8 }} onClick={() => history.push('/demos')}>All demos</IonButton>
      </IonContent>
    </IonPage>
  );
}
