import { IonContent, IonPage, IonButton, IonIcon } from '@ionic/react';
import { arrowForward, codeSlashOutline } from 'ionicons/icons';
import { useHistory } from 'react-router-dom';
import KamariMark from '../components/KamariMark';

export default function Welcome() {
  const history = useHistory();
  return (
    <IonPage>
      <IonContent fullscreen>
        <div className="kamari-hero kamari-pattern" style={{ minHeight: '62vh', padding: '28px' }}>
          <div style={{ paddingTop: 28, display: 'flex', justifyContent: 'center' }}>
            <KamariMark size={92} tone="gold" />
          </div>
          <div className="kamari-center" style={{ marginTop: 26 }}>
            <p className="kamari-eyebrow">African-built age verification</p>
            <h1 style={{ fontSize: '3rem', margin: '8px 0 0', color: 'var(--kamari-cream)' }}>
              Kámárí
            </h1>
            <p style={{ maxWidth: 320, margin: '14px auto 0', color: 'rgba(246,239,226,.86)', lineHeight: 1.5 }}>
              A respectful age check, tuned for African faces and skin tones — your photo
              is never stored.
            </p>
            <div style={{ marginTop: 18, display: 'flex', justifyContent: 'center' }}>
              <span className="kamari-badge on-dark">📷 Photo never stored</span>
            </div>
          </div>
        </div>

        <div className="kamari-pad kamari-stack">
          <div className="kamari-kente" />
          <IonButton
            expand="block"
            className="kamari-btn"
            color="secondary"
            onClick={() => history.push('/consent')}
          >
            Begin age check
            <IonIcon slot="end" icon={arrowForward} />
          </IonButton>
          <IonButton
            expand="block"
            fill="clear"
            color="primary"
            onClick={() => history.push('/developer')}
          >
            <IonIcon slot="start" icon={codeSlashOutline} />
            I’m a developer
          </IonButton>
          <p className="kamari-muted kamari-center" style={{ fontSize: '.8rem' }}>
            An estimate, not a legal determination.
          </p>
        </div>
      </IonContent>
    </IonPage>
  );
}
