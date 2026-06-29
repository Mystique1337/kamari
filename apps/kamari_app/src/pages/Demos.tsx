import {
  IonContent, IonPage, IonHeader, IonToolbar, IonTitle, IonButtons, IonBackButton,
  IonIcon, IonButton,
} from '@ionic/react';
import { arrowForward } from 'ionicons/icons';
import { useHistory } from 'react-router-dom';
import { DEMO_LIST } from '../lib/demos';

export default function Demos() {
  const history = useHistory();
  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonButtons slot="start"><IonBackButton defaultHref="/welcome" /></IonButtons>
          <IonTitle>Live demos</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent className="kamari-pad">
        <p className="kamari-eyebrow">See it in action</p>
        <h2 style={{ marginTop: 6, color: 'var(--kamari-cream)' }}>Three apps, one age gate</h2>
        <p style={{ color: 'rgba(246,239,226,.82)', maxWidth: 600 }}>
          Each demo is a mock partner app that calls the Kamari API and allows or restricts entry
          based on the decision. Try one with a selfie or an uploaded photo.
        </p>
        <div className="kamari-stack" style={{ marginTop: 20 }}>
          {DEMO_LIST.map((d) => (
            <button key={d.kind} onClick={() => history.push(`/demo/${d.kind}`)}
              className="kamari-card kamari-pad" style={{ textAlign: 'left', cursor: 'pointer', display: 'flex', gap: 14, alignItems: 'center', border: 'none', width: '100%' }}>
              <div style={{ width: 44, height: 44, borderRadius: 12, background: d.accent, display: 'grid', placeItems: 'center', flexShrink: 0 }}>
                <IonIcon icon={d.icon} style={{ color: '#fff', fontSize: 24 }} />
              </div>
              <div style={{ flex: 1 }}>
                <strong style={{ fontSize: '1.05rem' }}>{d.name}</strong>
                <p className="kamari-muted" style={{ margin: '2px 0 0', fontSize: '.9rem' }}>{d.tagline}</p>
              </div>
              <IonIcon icon={arrowForward} style={{ color: 'var(--kamari-indigo)' }} />
            </button>
          ))}
        </div>
        <IonButton expand="block" fill="clear" style={{ marginTop: 18 }} onClick={() => history.push('/docs')}>
          See how the integration works
        </IonButton>
      </IonContent>
    </IonPage>
  );
}
