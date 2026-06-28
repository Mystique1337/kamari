import {
  IonContent, IonPage, IonHeader, IonToolbar, IonTitle, IonButtons, IonBackButton,
  IonButton, IonIcon, IonInput, IonItem, IonSpinner, IonSegment, IonSegmentButton, IonLabel,
} from '@ionic/react';
import { logInOutline, personAddOutline, mailOutline, lockClosedOutline } from 'ionicons/icons';
import { useState } from 'react';
import { useHistory } from 'react-router-dom';
import { useAuth } from '../lib/auth';
import { sendWelcome } from '../lib/api';

export default function Login() {
  const { configured, signIn, signUp } = useAuth();
  const history = useHistory();
  const [mode, setMode] = useState<'signin' | 'signup'>('signin');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const submit = async () => {
    setError(null); setNotice(null);
    if (!email || !password) { setError('Enter your email and password.'); return; }
    setBusy(true);
    try {
      if (mode === 'signin') {
        await signIn(email, password);
        history.replace('/developer');
      } else {
        const { needsConfirmation } = await signUp(email, password);
        // Send our welcome email via n8n regardless of confirmation state.
        await sendWelcome(email);
        if (needsConfirmation) {
          setNotice('Account created. We sent you a welcome email. Confirm your address, then sign in.');
          setMode('signin');
        } else {
          history.replace('/developer');
        }
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Something went wrong.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonButtons slot="start"><IonBackButton defaultHref="/welcome" /></IonButtons>
          <IonTitle>Developer access</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent className="kamari-bg kamari-pad">
        <p className="kamari-eyebrow" style={{ color: 'var(--kamari-terracotta)' }}>Kamari for developers</p>
        <h2 style={{ marginTop: 6 }}>
          {mode === 'signin' ? 'Welcome back' : 'Create your account'}
        </h2>
        <p className="kamari-muted" style={{ marginTop: 4 }}>
          Manage API keys and see your usage. Age checks for end users do not need an account.
        </p>

        {!configured && (
          <div className="kamari-card kamari-pad" style={{ marginTop: 16, color: 'var(--kamari-ink)' }}>
            Auth is not configured in this build. Set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY.
          </div>
        )}

        <IonSegment
          value={mode}
          style={{ margin: '18px 0' }}
          onIonChange={(e) => setMode((e.detail.value as 'signin' | 'signup') ?? 'signin')}
        >
          <IonSegmentButton value="signin"><IonLabel>Sign in</IonLabel></IonSegmentButton>
          <IonSegmentButton value="signup"><IonLabel>Sign up</IonLabel></IonSegmentButton>
        </IonSegment>

        <div className="kamari-stack">
          <IonItem className="kamari-card">
            <IonIcon icon={mailOutline} slot="start" style={{ color: 'var(--kamari-indigo)' }} />
            <IonInput
              type="email" placeholder="you@company.com" value={email}
              autocomplete="email"
              onIonInput={(e) => setEmail(e.detail.value ?? '')}
            />
          </IonItem>
          <IonItem className="kamari-card">
            <IonIcon icon={lockClosedOutline} slot="start" style={{ color: 'var(--kamari-indigo)' }} />
            <IonInput
              type="password" placeholder="Password" value={password}
              autocomplete={mode === 'signin' ? 'current-password' : 'new-password'}
              onIonInput={(e) => setPassword(e.detail.value ?? '')}
            />
          </IonItem>
        </div>

        {error && <p style={{ color: '#B83A2E', fontSize: '.9rem', marginTop: 12 }}>{error}</p>}
        {notice && <p style={{ color: 'var(--kamari-green)', fontSize: '.9rem', marginTop: 12 }}>{notice}</p>}

        <IonButton
          expand="block" className="kamari-btn" color="secondary"
          style={{ marginTop: 18 }} disabled={busy || !configured} onClick={submit}
        >
          {busy ? <IonSpinner name="crescent" /> : (
            <>
              <IonIcon slot="start" icon={mode === 'signin' ? logInOutline : personAddOutline} />
              {mode === 'signin' ? 'Sign in' : 'Create account'}
            </>
          )}
        </IonButton>
      </IonContent>
    </IonPage>
  );
}
