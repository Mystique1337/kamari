import {
  IonContent, IonPage, IonHeader, IonToolbar, IonTitle, IonButtons, IonBackButton,
  IonList, IonItem, IonLabel, IonNote, IonSpinner, IonBadge,
} from '@ionic/react';
import { useEffect } from 'react';
import { useHistory } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { usageLogs } from '../lib/api';
import { useAuth } from '../lib/auth';

const TONE: Record<string, string> = {
  allow: 'success', block: 'danger', secondary_check: 'warning', recapture: 'medium',
};

export default function UsageLogs() {
  const history = useHistory();
  const { configured, loading, session, getToken } = useAuth();
  const token = getToken();

  useEffect(() => {
    if (configured && !loading && !session) history.replace('/login');
  }, [configured, loading, session, history]);

  const { data: logs, isLoading } = useQuery({
    queryKey: ['usage-logs', token],
    queryFn: () => usageLogs(token as string, 100),
    enabled: Boolean(token),
  });

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonButtons slot="start"><IonBackButton defaultHref="/developer" /></IonButtons>
          <IonTitle>Usage logs</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent className="kamari-bg kamari-pad">
        <p className="kamari-muted" style={{ marginTop: 0 }}>
          Recent age checks made with your API keys. Metadata only. No images are ever stored.
        </p>
        {isLoading ? (
          <div style={{ textAlign: 'center', marginTop: 30 }}><IonSpinner name="crescent" /></div>
        ) : (
          <IonList inset>
            {(logs ?? []).length === 0 && (
              <IonItem><IonLabel className="kamari-muted">No requests yet. Calls made with your API key will appear here.</IonLabel></IonItem>
            )}
            {(logs ?? []).map((l) => (
              <IonItem key={l.request_id}>
                <IonLabel>
                  <h2 style={{ fontFamily: 'monospace', fontSize: '.85rem' }}>{l.request_id}</h2>
                  <IonNote>
                    {l.reason_code.replaceAll('_', ' ').toLowerCase()} · {new Date(l.created_at).toLocaleString()}
                  </IonNote>
                </IonLabel>
                <IonBadge slot="end" color={TONE[l.decision] ?? 'medium'}>{l.decision}</IonBadge>
              </IonItem>
            ))}
          </IonList>
        )}
      </IonContent>
    </IonPage>
  );
}
