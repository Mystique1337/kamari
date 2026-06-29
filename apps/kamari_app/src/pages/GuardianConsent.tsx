import {
  IonContent, IonPage, IonHeader, IonToolbar, IonTitle, IonButtons, IonBackButton,
  IonButton, IonIcon, IonInput, IonItem, IonSpinner,
} from '@ionic/react';
import { mailOutline, keypadOutline, checkmarkCircle, shieldCheckmark } from 'ionicons/icons';
import { useState } from 'react';
import { useLocation, useHistory } from 'react-router-dom';
import { guardianRequest, guardianVerify } from '../lib/api';

// Two roles, one page:
//  - With ?session=... (opened from the guardian's email): enter the code to approve.
//  - Without a session (in-app, after a block): enter a guardian email to start the check,
//    then enter the code the guardian receives.
export default function GuardianConsent() {
  const loc = useLocation();
  const history = useHistory();
  const urlSession = new URLSearchParams(loc.search).get('session');

  const [guardianEmail, setGuardianEmail] = useState('');
  const [sessionId, setSessionId] = useState<string | null>(urlSession);
  const [code, setCode] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [approved, setApproved] = useState(false);

  const startRequest = async () => {
    setError(null);
    if (!guardianEmail) { setError('Enter a guardian email address.'); return; }
    setBusy(true);
    try {
      const { session_id } = await guardianRequest(guardianEmail, 'Kamari');
      setSessionId(session_id);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not start the guardian check.');
    } finally { setBusy(false); }
  };

  const verify = async () => {
    setError(null);
    if (!sessionId || !code) { setError('Enter the 6 digit code.'); return; }
    setBusy(true);
    try {
      const { approved: ok } = await guardianVerify(sessionId, code.trim());
      setApproved(ok);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Verification failed.');
    } finally { setBusy(false); }
  };

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonButtons slot="start"><IonBackButton defaultHref="/welcome" /></IonButtons>
          <IonTitle>Guardian check</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent className="kamari-pad">
        {approved ? (
          <div className="kamari-center" style={{ marginTop: 48 }}>
            <IonIcon icon={checkmarkCircle} style={{ fontSize: 72, color: 'var(--kamari-green)' }} />
            <h2>Guardian approved</h2>
            <p className="kamari-muted" style={{ maxWidth: 300, margin: '8px auto 0' }}>
              A guardian has approved this age check. You can continue.
            </p>
            <IonButton className="kamari-btn" color="secondary" style={{ marginTop: 20 }} onClick={() => history.replace('/welcome')}>
              <IonIcon slot="start" icon={shieldCheckmark} /> Continue
            </IonButton>
          </div>
        ) : (
          <>
            <p className="kamari-eyebrow" style={{ color: 'var(--kamari-terracotta)' }}>Parental consent</p>
            <h2 style={{ marginTop: 6 }}>
              {sessionId ? 'Enter the guardian code' : 'Ask a guardian to approve'}
            </h2>
            <p className="kamari-muted" style={{ marginTop: 4 }}>
              {sessionId
                ? 'A 6 digit code was sent to the guardian email. Enter it here to approve.'
                : 'We will email a one time code to a guardian. They review and approve this age check.'}
            </p>

            {!sessionId && (
              <>
                <IonItem className="kamari-card" style={{ marginTop: 16 }}>
                  <IonIcon icon={mailOutline} slot="start" style={{ color: 'var(--kamari-indigo)' }} />
                  <IonInput
                    type="email" placeholder="guardian@email.com" value={guardianEmail}
                    onIonInput={(e) => setGuardianEmail(e.detail.value ?? '')}
                  />
                </IonItem>
                <IonButton expand="block" className="kamari-btn" color="secondary" style={{ marginTop: 16 }} disabled={busy} onClick={startRequest}>
                  {busy ? <IonSpinner name="crescent" /> : 'Send guardian code'}
                </IonButton>
              </>
            )}

            {sessionId && (
              <>
                <IonItem className="kamari-card" style={{ marginTop: 16 }}>
                  <IonIcon icon={keypadOutline} slot="start" style={{ color: 'var(--kamari-indigo)' }} />
                  <IonInput
                    type="tel" inputmode="numeric" maxlength={6} placeholder="123456" value={code}
                    onIonInput={(e) => setCode(e.detail.value ?? '')}
                  />
                </IonItem>
                <IonButton expand="block" className="kamari-btn" color="secondary" style={{ marginTop: 16 }} disabled={busy} onClick={verify}>
                  {busy ? <IonSpinner name="crescent" /> : 'Verify code'}
                </IonButton>
              </>
            )}

            {error && <p style={{ color: '#B83A2E', fontSize: '.9rem', marginTop: 12 }}>{error}</p>}
          </>
        )}
      </IonContent>
    </IonPage>
  );
}
