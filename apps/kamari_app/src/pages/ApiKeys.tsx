import {
  IonContent, IonPage, IonHeader, IonToolbar, IonTitle, IonButtons, IonBackButton,
  IonButton, IonIcon, IonList, IonItem, IonLabel, IonNote,
} from '@ionic/react';
import { addOutline, trashOutline, keyOutline } from 'ionicons/icons';
import { useState } from 'react';

interface ApiKey {
  id: string;
  name: string;
  prefix: string;
  scopes: string;
  rpm: number;
  created: string;
}

const SEED: ApiKey[] = [
  { id: '1', name: 'Production', prefix: 'kmr_live_a93f', scopes: 'age:estimate, age:explain', rpm: 120, created: '2026-06-20' },
  { id: '2', name: 'Sandbox', prefix: 'kmr_test_7c10', scopes: 'age:estimate', rpm: 30, created: '2026-06-22' },
];

export default function ApiKeys() {
  const [keys, setKeys] = useState<ApiKey[]>(SEED);

  const create = () => {
    const rand = Math.random().toString(36).slice(2, 6);
    setKeys((k) => [
      ...k,
      { id: String(Date.now()), name: 'New key', prefix: `kmr_live_${rand}`, scopes: 'age:estimate', rpm: 60, created: '2026-06-28' },
    ]);
  };
  const revoke = (id: string) => setKeys((k) => k.filter((x) => x.id !== id));

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
          Keys authenticate calls to the Kámárí gateway. Secrets are shown once on creation.
        </p>

        <IonList inset>
          {keys.map((k) => (
            <IonItem key={k.id}>
              <IonIcon icon={keyOutline} slot="start" style={{ color: 'var(--kamari-indigo)' }} />
              <IonLabel>
                <h2>{k.name}</h2>
                <p style={{ fontFamily: 'monospace' }}>{k.prefix}••••••</p>
                <IonNote>{k.scopes} · {k.rpm} rpm · {k.created}</IonNote>
              </IonLabel>
              <IonButton fill="clear" color="danger" slot="end" onClick={() => revoke(k.id)}>
                <IonIcon icon={trashOutline} />
              </IonButton>
            </IonItem>
          ))}
        </IonList>

        <IonButton expand="block" className="kamari-btn" color="secondary" onClick={create}>
          <IonIcon slot="start" icon={addOutline} />
          Create API key
        </IonButton>
      </IonContent>
    </IonPage>
  );
}
