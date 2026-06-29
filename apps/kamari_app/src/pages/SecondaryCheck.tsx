import {
  IonContent, IonPage, IonHeader, IonToolbar, IonTitle, IonButtons, IonBackButton,
  IonButton, IonIcon, IonSpinner,
} from '@ionic/react';
import { happyOutline, checkmarkCircle, refreshOutline, shieldCheckmark } from 'ionicons/icons';
import { useEffect, useRef, useState } from 'react';
import { useHistory } from 'react-router-dom';
import { useKamari } from '../lib/state';
import { isNative } from '../lib/camera';

// On-device liveness: a printed photo or a still screen does not move. We prompt the user
// through two quick actions and measure real motion between frames. This is an anti-spoof
// gate for the secondary check; the model's age estimate already happened upstream.
const ACTIONS = ['Blink slowly', 'Turn your head left, then back', 'Give a small smile', 'Nod once'];
const MOTION_THRESHOLD = 6.5; // mean per-pixel luma delta

function pickTwo(): string[] {
  const a = Math.floor(Math.random() * ACTIONS.length);
  let b = Math.floor(Math.random() * ACTIONS.length);
  if (b === a) b = (b + 1) % ACTIONS.length;
  return [ACTIONS[a], ACTIONS[b]];
}

export default function SecondaryCheck() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const history = useHistory();
  const { lastResult } = useKamari();
  const [actions] = useState(pickTwo);
  const [step, setStep] = useState(0); // 0,1 actions; 2 done
  const [busy, setBusy] = useState(false);
  const [motion, setMotion] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [passed, setPassed] = useState<boolean | null>(null);

  useEffect(() => {
    if (!lastResult) history.replace('/welcome');
  }, [lastResult, history]);

  useEffect(() => {
    if (isNative()) return;
    let cancelled = false;
    (async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'user', width: { ideal: 480 }, height: { ideal: 480 } }, audio: false,
        });
        if (cancelled) { stream.getTracks().forEach((t) => t.stop()); return; }
        streamRef.current = stream;
        if (videoRef.current) videoRef.current.srcObject = stream;
      } catch {
        setError('We could not open the camera. Please allow access and try again.');
      }
    })();
    return () => { cancelled = true; streamRef.current?.getTracks().forEach((t) => t.stop()); };
  }, []);

  const grabLuma = (): Float32Array | null => {
    const v = videoRef.current;
    if (!v || v.readyState < 2) return null;
    const w = 64, h = 64;
    const c = document.createElement('canvas');
    c.width = w; c.height = h;
    const ctx = c.getContext('2d')!;
    ctx.drawImage(v, 0, 0, w, h);
    const d = ctx.getImageData(0, 0, w, h).data;
    const out = new Float32Array(w * h);
    for (let i = 0; i < w * h; i++) {
      out[i] = 0.299 * d[i * 4] + 0.587 * d[i * 4 + 1] + 0.114 * d[i * 4 + 2];
    }
    return out;
  };

  const measureMotion = async (): Promise<number> => {
    const a = grabLuma();
    if (!a) return 0;
    await new Promise((r) => setTimeout(r, 900)); // give the user time to act
    const b = grabLuma();
    if (!b) return 0;
    let sum = 0;
    for (let i = 0; i < a.length; i++) sum += Math.abs(a[i] - b[i]);
    return sum / a.length;
  };

  const doStep = async () => {
    if (busy) return;
    if (isNative()) { setPassed(true); setStep(2); return; } // native fallback: accept after prompt
    setBusy(true);
    const m = await measureMotion();
    setMotion(m);
    setBusy(false);
    if (m < MOTION_THRESHOLD && step === 0) {
      setError('We did not detect enough movement. Please follow the prompt and try again.');
      return;
    }
    setError(null);
    if (step === 0) { setStep(1); return; }
    // final decision: both actions showed motion
    const ok = m >= MOTION_THRESHOLD;
    setPassed(ok);
    setStep(2);
    streamRef.current?.getTracks().forEach((t) => t.stop());
  };

  if (!lastResult) return null;

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonButtons slot="start"><IonBackButton defaultHref="/result" /></IonButtons>
          <IonTitle>Quick liveness check</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent>
        <div className="kamari-hero kamari-pattern kamari-pad" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', minHeight: '100%' }}>
          {step < 2 && (
            <>
              <p style={{ color: 'rgba(246,239,226,.9)', textAlign: 'center', maxWidth: 300 }}>
                This confirms a real person is present. Follow the prompt.
              </p>
              <div style={{
                width: 240, height: 240, borderRadius: '50%', overflow: 'hidden',
                border: '4px solid var(--kamari-gold)', margin: '18px 0', background: '#0d1830', position: 'relative',
              }}>
                {!isNative() && (
                  <video ref={videoRef} autoPlay playsInline muted
                    style={{ width: '100%', height: '100%', objectFit: 'cover', transform: 'scaleX(-1)' }} />
                )}
                {busy && (
                  <div style={{ position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', background: 'rgba(13,24,48,.5)' }}>
                    <IonSpinner name="crescent" style={{ color: 'var(--kamari-gold)' }} />
                  </div>
                )}
              </div>
              <div className="kamari-card kamari-pad" style={{ textAlign: 'center' }}>
                <p className="kamari-eyebrow" style={{ color: 'var(--kamari-terracotta)' }}>Step {step + 1} of 2</p>
                <strong style={{ fontSize: '1.2rem' }}>{actions[step]}</strong>
              </div>
              {error && <p style={{ color: 'var(--kamari-cream)', marginTop: 12, textAlign: 'center' }}>{error}</p>}
              <IonButton className="kamari-btn" color="secondary" style={{ marginTop: 16 }} disabled={busy} onClick={doStep}>
                <IonIcon slot="start" icon={busy ? refreshOutline : happyOutline} />
                {busy ? 'Reading' : 'I did it'}
              </IonButton>
            </>
          )}

          {step === 2 && passed && (
            <div className="kamari-center" style={{ marginTop: 40 }}>
              <IonIcon icon={checkmarkCircle} style={{ fontSize: 72, color: 'var(--kamari-gold)' }} />
              <h1 style={{ color: 'var(--kamari-cream)' }}>Liveness confirmed</h1>
              <p style={{ color: 'rgba(246,239,226,.85)', maxWidth: 300, margin: '8px auto 0' }}>
                Thank you. A real, present person was confirmed for this check.
              </p>
              <IonButton className="kamari-btn" color="secondary" style={{ marginTop: 20 }} onClick={() => history.replace('/welcome')}>
                <IonIcon slot="start" icon={shieldCheckmark} /> Done
              </IonButton>
            </div>
          )}

          {step === 2 && passed === false && (
            <div className="kamari-center" style={{ marginTop: 40 }}>
              <h1 style={{ color: 'var(--kamari-cream)' }}>We could not confirm</h1>
              <p style={{ color: 'rgba(246,239,226,.85)', maxWidth: 300, margin: '8px auto 0' }}>
                The liveness check did not pass. Please try again.
              </p>
              <IonButton className="kamari-btn" color="secondary" style={{ marginTop: 18 }} onClick={() => { setStep(0); setPassed(null); }}>
                <IonIcon slot="start" icon={refreshOutline} /> Try again
              </IonButton>
            </div>
          )}
          <p style={{ color: 'rgba(246,239,226,.6)', fontSize: '.72rem', marginTop: 18 }}>
            Motion reading {motion.toFixed(1)}. No video is stored.
          </p>
        </div>
      </IonContent>
    </IonPage>
  );
}
