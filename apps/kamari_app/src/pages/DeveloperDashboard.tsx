import {
  IonContent, IonPage, IonHeader, IonToolbar, IonTitle, IonButtons, IonBackButton,
  IonButton, IonIcon,
} from '@ionic/react';
import { keyOutline, pulseOutline, shieldCheckmarkOutline, serverOutline } from 'ionicons/icons';
import { useHistory } from 'react-router-dom';
import { apiMode } from '../lib/api';

const STATS = [
  { label: 'Requests (24h)', value: '1,284' },
  { label: 'Allow rate', value: '71%' },
  { label: 'Secondary checks', value: '18%' },
  { label: 'p95 latency', value: '340 ms' },
];

export default function DeveloperDashboard() {
  const history = useHistory();
  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonButtons slot="start"><IonBackButton defaultHref="/welcome" /></IonButtons>
          <IonTitle>Developer</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent className="kamari-bg kamari-pad">
        <div className="kamari-card kamari-pad" style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <IonIcon icon={serverOutline} style={{ fontSize: 24, color: 'var(--kamari-indigo)' }} />
          <div style={{ flex: 1 }}>
            <strong>API mode</strong>
            <p className="kamari-muted" style={{ margin: '2px 0 0', fontSize: '.85rem' }}>
              {apiMode === 'live'
                ? 'Live — calling your configured gateway.'
                : 'Mock — set VITE_KAMARI_API_URL to go live.'}
            </p>
          </div>
          <span className={`kamari-badge ${apiMode === 'live' ? '' : ''}`}>{apiMode}</span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginTop: 14 }}>
          {STATS.map((s) => (
            <div key={s.label} className="kamari-card" style={{ padding: 16 }}>
              <div style={{ fontFamily: 'var(--kamari-font-display)', fontSize: '1.6rem' }}>{s.value}</div>
              <div className="kamari-muted" style={{ fontSize: '.8rem' }}>{s.label}</div>
            </div>
          ))}
        </div>

        <div className="kamari-card kamari-pad" style={{ marginTop: 14, display: 'flex', gap: 12 }}>
          <IonIcon icon={shieldCheckmarkOutline} style={{ fontSize: 24, color: 'var(--kamari-green)' }} />
          <div>
            <strong>Fairness-tested</strong>
            <p className="kamari-muted" style={{ margin: '2px 0 0', fontSize: '.85rem' }}>
              Benchmarked on the Kámárí-Safe Open set across skin bands and the 13–21 boundary.
            </p>
          </div>
        </div>

        <div className="kamari-kente" style={{ margin: '20px 0' }} />

        <IonButton expand="block" className="kamari-btn" color="primary" onClick={() => history.push('/developer/keys')}>
          <IonIcon slot="start" icon={keyOutline} />
          Manage API keys
        </IonButton>
        <IonButton expand="block" fill="outline" color="primary">
          <IonIcon slot="start" icon={pulseOutline} />
          View usage logs
        </IonButton>
      </IonContent>
    </IonPage>
  );
}
