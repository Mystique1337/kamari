import {
  IonContent, IonPage, IonHeader, IonToolbar, IonTitle, IonButtons, IonBackButton,
  IonIcon, IonButton,
} from '@ionic/react';
import { lockClosedOutline, checkmarkCircle, closeCircle, refreshOutline, homeOutline } from 'ionicons/icons';
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

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar style={{ '--background': demo.accent, '--color': '#fff' } as CSSProperties}>
          <IonButtons slot="start"><IonBackButton defaultHref="/demos" /></IonButtons>
          <IonTitle>{demo.name}</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent className="kamari-pad">
        {/* Mock partner-app header */}
        <div style={{ background: demo.accent, color: '#fff', borderRadius: 'var(--kamari-radius)', padding: 22, marginBottom: 18 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <IonIcon icon={demo.icon} style={{ fontSize: 30 }} />
            <div>
              <strong style={{ fontSize: '1.3rem' }}>{demo.name}</strong>
              <p style={{ margin: 0, opacity: .85, fontSize: '.9rem' }}>{demo.tagline}</p>
            </div>
          </div>
        </div>

        {!result && (
          <div className="kamari-card kamari-pad kamari-center">
            <IonIcon icon={lockClosedOutline} style={{ fontSize: 34, color: demo.accent }} />
            <h3 style={{ margin: '10px 0 4px' }}>Age check required</h3>
            <p className="kamari-muted" style={{ marginTop: 0 }}>{demo.gate}</p>
            <div style={{ marginTop: 14 }}>
              <AgeGate onResult={setResult} />
            </div>
          </div>
        )}

        {result && allowed && (
          <div className="kamari-card kamari-pad kamari-center">
            <IonIcon icon={checkmarkCircle} style={{ fontSize: 56, color: 'var(--kamari-green)' }} />
            <h3 style={{ margin: '10px 0 4px' }}>Welcome to {demo.name}</h3>
            <p className="kamari-muted">{demo.allowed}</p>
            <p style={{ fontSize: '.8rem' }}>Estimated age {result.estimated_age}. Decision: allow.</p>
            <IonButton fill="clear" onClick={reset}><IonIcon slot="start" icon={refreshOutline} /> Run again</IonButton>
          </div>
        )}

        {result && !allowed && (
          <div className="kamari-card kamari-pad kamari-center">
            <IonIcon icon={closeCircle} style={{ fontSize: 56, color: '#B83A2E' }} />
            <h3 style={{ margin: '10px 0 4px' }}>
              {result.decision === 'block' ? 'Entry restricted' : 'One more step'}
            </h3>
            <p className="kamari-muted">{result.message}</p>
            <p style={{ fontSize: '.8rem' }}>Decision: {result.decision.replaceAll('_', ' ')}.</p>
            <IonButton className="kamari-btn" color="secondary" onClick={reset}>
              <IonIcon slot="start" icon={refreshOutline} /> Try again
            </IonButton>
          </div>
        )}

        <IonButton expand="block" fill="clear" style={{ marginTop: 16 }} onClick={() => history.push('/demos')}>
          <IonIcon slot="start" icon={homeOutline} /> All demos
        </IonButton>
      </IonContent>
    </IonPage>
  );
}
