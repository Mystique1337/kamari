import {
  IonContent, IonPage, IonHeader, IonToolbar, IonTitle, IonButtons, IonBackButton,
  IonList, IonItem, IonLabel, IonNote, IonBadge, IonIcon, IonSkeletonText,
} from '@ionic/react';
import { chevronDownOutline, chevronUpOutline } from 'ionicons/icons';
import { useEffect, useState } from 'react';
import { useHistory } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { usageLogs, type UsageLog } from '../lib/api';
import { useAuth } from '../lib/auth';

const TONE: Record<string, string> = {
  allow: 'success', block: 'danger', secondary_check: 'warning', recapture: 'medium',
};

const pct = (x: number | null | undefined) => (x === null || x === undefined ? '-' : `${Math.round(x * 100)}%`);

export default function UsageLogs() {
  const history = useHistory();
  const { configured, loading, session, getToken } = useAuth();
  const token = getToken();
  const [open, setOpen] = useState<Record<string, boolean>>({});

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
          Recent age checks made with your API keys. Tap a row to see the full decision trace.
          Metadata only. No images are ever stored.
        </p>
        {isLoading ? (
          <div className="kamari-stack">
            {[0, 1, 2, 3, 4].map((i) => (
              <div key={i} className="kamari-card kamari-pad">
                <IonSkeletonText animated style={{ width: '60%', height: 14 }} />
                <IonSkeletonText animated style={{ width: '40%', height: 12 }} />
              </div>
            ))}
          </div>
        ) : (
          <IonList inset>
            {(logs ?? []).length === 0 && (
              <IonItem><IonLabel className="kamari-muted">No requests yet. Calls made with your API key will appear here.</IonLabel></IonItem>
            )}
            {(logs ?? []).map((l: UsageLog) => {
              const isOpen = open[l.request_id];
              return (
                <div key={l.request_id}>
                  <IonItem button detail={false} onClick={() => setOpen((o) => ({ ...o, [l.request_id]: !o[l.request_id] }))}>
                    <IonLabel>
                      <h2 style={{ fontFamily: 'monospace', fontSize: '.85rem' }}>{l.request_id}</h2>
                      <IonNote>{l.reason_code.replaceAll('_', ' ').toLowerCase()} · {new Date(l.created_at).toLocaleString()}</IonNote>
                    </IonLabel>
                    <IonBadge slot="end" color={TONE[l.decision] ?? 'medium'}>{l.decision}</IonBadge>
                    <IonIcon slot="end" icon={isOpen ? chevronUpOutline : chevronDownOutline} />
                  </IonItem>
                  {isOpen && (
                    <div style={{ padding: '8px 18px 14px', fontSize: '.85rem' }}>
                      <Trace k="Endpoint" v={l.endpoint} />
                      <Trace k="Estimated age" v={l.estimated_age ?? '-'} />
                      <Trace k="Under-18 probability" v={pct(l.p_under_18)} />
                      <Trace k="Confidence" v={l.uncertainty === null || l.uncertainty === undefined ? '-' : `${Math.round((1 - l.uncertainty) * 100)}%`} />
                      <Trace k="Face quality" v={pct(l.face_quality)} />
                      <Trace k="Model" v={l.model_version ?? '-'} />
                      <Trace k="Retention" v={(l.retention_policy ?? 'image_not_stored').replaceAll('_', ' ')} />
                    </div>
                  )}
                </div>
              );
            })}
          </IonList>
        )}
      </IonContent>
    </IonPage>
  );
}

function Trace({ k, v }: { k: string; v: string | number }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', borderBottom: '1px solid rgba(120,120,120,.12)' }}>
      <span className="kamari-muted">{k}</span>
      <span style={{ fontWeight: 600 }}>{v}</span>
    </div>
  );
}
