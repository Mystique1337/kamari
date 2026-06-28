import {
  IonContent, IonPage, IonHeader, IonToolbar, IonTitle, IonButtons, IonBackButton,
  IonButton, IonIcon, IonSpinner,
} from '@ionic/react';
import {
  keyOutline, pulseOutline, shieldCheckmarkOutline, serverOutline, logOutOutline,
} from 'ionicons/icons';
import { useEffect } from 'react';
import { useHistory } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { apiMode, usageSummary } from '../lib/api';
import { useAuth } from '../lib/auth';

export default function DeveloperDashboard() {
  const history = useHistory();
  const { configured, loading, session, email, getToken, signOut } = useAuth();

  // Gate: a signed-in account is required for the developer area.
  useEffect(() => {
    if (configured && !loading && !session) history.replace('/login');
  }, [configured, loading, session, history]);

  const token = getToken();
  const { data: usage, isLoading } = useQuery({
    queryKey: ['usage-summary', token],
    queryFn: () => usageSummary(token as string),
    enabled: Boolean(token),
  });

  const stats = [
    { label: 'Requests', value: usage ? String(usage.total) : '0' },
    { label: 'Allow rate', value: usage ? `${Math.round(usage.allow_rate * 100)}%` : '0%' },
    { label: 'Secondary checks', value: usage ? String(usage.secondary_check) : '0' },
    { label: 'Blocks', value: usage ? String(usage.block) : '0' },
  ];

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonButtons slot="start"><IonBackButton defaultHref="/welcome" /></IonButtons>
          <IonTitle>Developer</IonTitle>
          <IonButtons slot="end">
            <IonButton onClick={async () => { await signOut(); history.replace('/welcome'); }}>
              <IonIcon slot="icon-only" icon={logOutOutline} />
            </IonButton>
          </IonButtons>
        </IonToolbar>
      </IonHeader>
      <IonContent className="kamari-bg kamari-pad">
        {email && (
          <p className="kamari-muted" style={{ marginTop: 0 }}>Signed in as <strong>{email}</strong></p>
        )}

        <div className="kamari-card kamari-pad" style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <IonIcon icon={serverOutline} style={{ fontSize: 24, color: 'var(--kamari-indigo)' }} />
          <div style={{ flex: 1 }}>
            <strong>API mode</strong>
            <p className="kamari-muted" style={{ margin: '2px 0 0', fontSize: '.85rem' }}>
              {apiMode === 'live' ? 'Live. Calling your configured gateway.' : 'Mock. Set VITE_KAMARI_API_URL to go live.'}
            </p>
          </div>
          <span className="kamari-badge">{apiMode}</span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginTop: 14 }}>
          {stats.map((s) => (
            <div key={s.label} className="kamari-card" style={{ padding: 16 }}>
              <div style={{ fontFamily: 'var(--kamari-font-display)', fontSize: '1.6rem' }}>
                {isLoading ? <IonSpinner name="dots" /> : s.value}
              </div>
              <div className="kamari-muted" style={{ fontSize: '.8rem' }}>{s.label}</div>
            </div>
          ))}
        </div>

        <div className="kamari-card kamari-pad" style={{ marginTop: 14, display: 'flex', gap: 12 }}>
          <IonIcon icon={shieldCheckmarkOutline} style={{ fontSize: 24, color: 'var(--kamari-green)' }} />
          <div>
            <strong>Fairness tested</strong>
            <p className="kamari-muted" style={{ margin: '2px 0 0', fontSize: '.85rem' }}>
              Benchmarked across skin bands and the 13 to 21 boundary, with a minor pass through safety metric.
            </p>
          </div>
        </div>

        <div className="kamari-kente" style={{ margin: '20px 0' }} />

        <IonButton expand="block" className="kamari-btn" color="primary" onClick={() => history.push('/developer/keys')}>
          <IonIcon slot="start" icon={keyOutline} /> Manage API keys
        </IonButton>
        <IonButton expand="block" fill="outline" color="primary" onClick={() => history.push('/developer/usage')}>
          <IonIcon slot="start" icon={pulseOutline} /> View usage logs
        </IonButton>
      </IonContent>
    </IonPage>
  );
}
