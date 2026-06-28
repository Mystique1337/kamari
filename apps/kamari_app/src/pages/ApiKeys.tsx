import {
  IonContent, IonPage, IonHeader, IonToolbar, IonTitle, IonButtons, IonBackButton,
  IonButton, IonIcon, IonList, IonItem, IonLabel, IonNote, IonSpinner, IonAlert,
} from '@ionic/react';
import { addOutline, trashOutline, keyOutline } from 'ionicons/icons';
import { useEffect, useState } from 'react';
import { useHistory } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { listKeys, createKey, revokeKey } from '../lib/api';
import { useAuth } from '../lib/auth';

export default function ApiKeys() {
  const history = useHistory();
  const { configured, loading, session, getToken } = useAuth();
  const qc = useQueryClient();
  const token = getToken();
  const [showCreate, setShowCreate] = useState(false);
  const [secret, setSecret] = useState<string | null>(null);

  useEffect(() => {
    if (configured && !loading && !session) history.replace('/login');
  }, [configured, loading, session, history]);

  const { data: keys, isLoading } = useQuery({
    queryKey: ['keys', token],
    queryFn: () => listKeys(token as string),
    enabled: Boolean(token),
  });

  const create = useMutation({
    mutationFn: (name: string) => createKey(token as string, name),
    onSuccess: (res) => {
      setSecret(res.api_key);
      qc.invalidateQueries({ queryKey: ['keys'] });
    },
  });

  const revoke = useMutation({
    mutationFn: (id: string) => revokeKey(token as string, id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['keys'] }),
  });

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonButtons slot="start"><IonBackButton defaultHref="/developer" /></IonButtons>
          <IonTitle>API keys</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent className="kamari-bg kamari-pad">
        <p className="kamari-muted" style={{ marginTop: 0 }}>
          Keys authenticate calls to the Kamari gateway. The secret is shown once on creation.
        </p>

        {isLoading ? (
          <div style={{ textAlign: 'center', marginTop: 30 }}><IonSpinner name="crescent" /></div>
        ) : (
          <IonList inset>
            {(keys ?? []).length === 0 && (
              <IonItem><IonLabel className="kamari-muted">No keys yet. Create your first one below.</IonLabel></IonItem>
            )}
            {(keys ?? []).map((k) => (
              <IonItem key={k.id}>
                <IonIcon icon={keyOutline} slot="start" style={{ color: 'var(--kamari-indigo)' }} />
                <IonLabel>
                  <h2>{k.name}</h2>
                  <IonNote>
                    {k.status} · {k.rate_limit_per_minute} rpm · {new Date(k.created_at).toLocaleDateString()}
                    {k.last_used_at ? ` · last used ${new Date(k.last_used_at).toLocaleDateString()}` : ''}
                  </IonNote>
                </IonLabel>
                {k.status === 'active' && (
                  <IonButton fill="clear" color="danger" slot="end" onClick={() => revoke.mutate(k.id)}>
                    <IonIcon icon={trashOutline} />
                  </IonButton>
                )}
              </IonItem>
            ))}
          </IonList>
        )}

        <IonButton expand="block" className="kamari-btn" color="secondary" onClick={() => setShowCreate(true)}>
          <IonIcon slot="start" icon={addOutline} /> Create API key
        </IonButton>

        <IonAlert
          isOpen={showCreate}
          header="Name your key"
          inputs={[{ name: 'name', type: 'text', placeholder: 'e.g. Production' }]}
          buttons={[
            { text: 'Cancel', role: 'cancel' },
            { text: 'Create', handler: (d) => { create.mutate((d.name || 'default').trim()); } },
          ]}
          onDidDismiss={() => setShowCreate(false)}
        />

        <IonAlert
          isOpen={Boolean(secret)}
          header="Copy your API key now"
          subHeader="This is the only time it is shown."
          message={secret ?? ''}
          buttons={[
            { text: 'Copy', handler: () => { if (secret) navigator.clipboard?.writeText(secret); } },
            { text: 'Done', role: 'cancel' },
          ]}
          onDidDismiss={() => setSecret(null)}
        />
      </IonContent>
    </IonPage>
  );
}
