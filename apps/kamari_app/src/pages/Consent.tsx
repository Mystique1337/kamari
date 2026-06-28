import {
  IonContent, IonPage, IonHeader, IonToolbar, IonTitle, IonButtons, IonBackButton,
  IonButton, IonIcon, IonCheckbox,
} from '@ionic/react';
import { lockClosedOutline, eyeOffOutline, personOutline, arrowForward } from 'ionicons/icons';
import { useState } from 'react';
import { useHistory } from 'react-router-dom';
import { useKamari } from '../lib/state';
import LocalePicker from '../components/LocalePicker';

const POINTS = [
  { icon: eyeOffOutline, title: 'Your photo is never stored', body: 'We process the image in the moment and delete it immediately. No image, no face print is kept.' },
  { icon: lockClosedOutline, title: 'Only a decision is logged', body: 'We keep the outcome and model version for safety auditing - never your face.' },
  { icon: personOutline, title: 'This is an estimate', body: 'Kámárí estimates age; it is not a legal age determination. Borderline cases get a second check.' },
];

export default function Consent() {
  const [agreed, setAgreed] = useState(false);
  const history = useHistory();
  const { acceptConsent } = useKamari();

  const proceed = () => {
    acceptConsent();
    history.push('/capture');
  };

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonButtons slot="start"><IonBackButton defaultHref="/welcome" /></IonButtons>
          <IonTitle>Before we start</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent className="kamari-bg kamari-pad">
        <p className="kamari-eyebrow" style={{ color: 'var(--kamari-terracotta)' }}>Privacy first</p>
        <h2 style={{ marginTop: 6 }}>How Kámárí treats your photo</h2>

        <div style={{ marginTop: 14 }}>
          <LocalePicker />
        </div>

        <div className="kamari-stack" style={{ marginTop: 18 }}>
          {POINTS.map((p) => (
            <div key={p.title} className="kamari-card" style={{ padding: 18, display: 'flex', gap: 14 }}>
              <IonIcon icon={p.icon} style={{ fontSize: 26, color: 'var(--kamari-indigo)', flexShrink: 0 }} />
              <div>
                <strong>{p.title}</strong>
                <p className="kamari-muted" style={{ margin: '4px 0 0', fontSize: '.9rem' }}>{p.body}</p>
              </div>
            </div>
          ))}
        </div>

        <label style={{ display: 'flex', gap: 12, alignItems: 'flex-start', margin: '22px 4px' }}>
          <IonCheckbox checked={agreed} onIonChange={(e) => setAgreed(e.detail.checked)} />
          <span style={{ fontSize: '.9rem' }}>
            I understand my photo is processed once and not stored, and I consent to this age check.
          </span>
        </label>

        <IonButton expand="block" className="kamari-btn" color="secondary" disabled={!agreed} onClick={proceed}>
          I agree - continue
          <IonIcon slot="end" icon={arrowForward} />
        </IonButton>
      </IonContent>
    </IonPage>
  );
}
