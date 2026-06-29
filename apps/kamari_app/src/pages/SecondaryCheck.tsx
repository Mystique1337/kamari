import {
  IonContent, IonPage, IonHeader, IonToolbar, IonTitle, IonButtons, IonBackButton,
  IonButton, IonIcon,
} from '@ionic/react';
import { checkmarkCircle, shieldCheckmark, happyOutline } from 'ionicons/icons';
import { useEffect, useRef, useState } from 'react';
import { useHistory } from 'react-router-dom';
import { useKamari } from '../lib/state';
import { isNative } from '../lib/camera';

// Easy liveness: the user just stays in frame and moves a little (blink, nod, or turn).
// We continuously measure motion and fill a progress ring; once enough real motion is seen
// it passes automatically. A printed photo or a still screen does not move, so it cannot pass.
const TARGET = 26;        // motion energy needed to pass (a few seconds of mild movement)
const PER_FRAME_CAP = 6;  // ignore huge jumps (lighting flashes) so it stays robust

export default function SecondaryCheck() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const history = useHistory();
  const { lastResult } = useKamari();
  const [progress, setProgress] = useState(0);
  const [passed, setPassed] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const prevRef = useRef<Float32Array | null>(null);
  const energyRef = useRef(0);
  const passedRef = useRef(false);

  useEffect(() => { if (!lastResult) history.replace('/welcome'); }, [lastResult, history]);

  useEffect(() => {
    if (isNative()) { setPassed(true); return; } // native fallback: accept (camera UI differs)
    let cancelled = false;
    (async () => {
      try {
        const s = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user', width: { ideal: 480 } }, audio: false });
        if (cancelled) { s.getTracks().forEach((t) => t.stop()); return; }
        streamRef.current = s;
        if (videoRef.current) videoRef.current.srcObject = s;
      } catch {
        setError('Allow camera access to do a quick presence check.');
      }
    })();
    return () => { cancelled = true; streamRef.current?.getTracks().forEach((t) => t.stop()); };
  }, []);

  useEffect(() => {
    if (isNative()) return;
    const grab = (): Float32Array | null => {
      const v = videoRef.current;
      if (!v || v.readyState < 2) return null;
      const n = 48;
      const c = document.createElement('canvas'); c.width = n; c.height = n;
      const ctx = c.getContext('2d'); if (!ctx) return null;
      const s = Math.min(v.videoWidth, v.videoHeight);
      ctx.drawImage(v, (v.videoWidth - s) / 2, (v.videoHeight - s) / 2, s, s, 0, 0, n, n);
      const d = ctx.getImageData(0, 0, n, n).data;
      const out = new Float32Array(n * n);
      for (let i = 0; i < n * n; i++) out[i] = 0.299 * d[i * 4] + 0.587 * d[i * 4 + 1] + 0.114 * d[i * 4 + 2];
      return out;
    };
    const id = setInterval(() => {
      if (passedRef.current) return;
      const cur = grab();
      const prev = prevRef.current;
      prevRef.current = cur;
      if (!cur || !prev) return;
      let sum = 0;
      for (let i = 0; i < cur.length; i++) sum += Math.abs(cur[i] - prev[i]);
      const motion = Math.min(PER_FRAME_CAP, sum / cur.length);
      energyRef.current += motion;
      const p = Math.min(100, (energyRef.current / TARGET) * 100);
      setProgress(p);
      if (energyRef.current >= TARGET) {
        passedRef.current = true;
        setPassed(true);
        streamRef.current?.getTracks().forEach((t) => t.stop());
      }
    }, 350);
    return () => clearInterval(id);
  }, []);

  if (!lastResult) return null;

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonButtons slot="start"><IonBackButton defaultHref="/result" /></IonButtons>
          <IonTitle>Quick presence check</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent>
        <div className="kamari-hero kamari-pattern kamari-pad" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', minHeight: '100%' }}>
          {!passed ? (
            <>
              <p style={{ color: 'rgba(246,239,226,.9)', textAlign: 'center', maxWidth: 320 }}>
                Look at the camera and move a little: blink, nod, or turn your head slowly. No tapping needed.
              </p>
              <div style={{
                width: 220, height: 220, borderRadius: '50%', overflow: 'hidden', margin: '18px 0',
                background: '#0d1830', position: 'relative',
                border: `5px solid var(--kamari-gold)`,
                boxShadow: `0 0 0 ${Math.round(progress / 12)}px rgba(232,184,75,.18)`,
                transition: 'box-shadow .2s',
              }}>
                <video ref={videoRef} autoPlay playsInline muted
                  style={{ width: '100%', height: '100%', objectFit: 'cover', transform: 'scaleX(-1)' }} />
              </div>
              {/* Progress bar */}
              <div style={{ width: 240, height: 8, borderRadius: 6, background: 'rgba(246,239,226,.18)', overflow: 'hidden' }}>
                <div style={{ width: `${progress}%`, height: '100%', background: 'var(--kamari-gold)', transition: 'width .2s' }} />
              </div>
              <p style={{ color: 'rgba(246,239,226,.7)', fontSize: '.8rem', marginTop: 10 }}>
                <IonIcon icon={happyOutline} /> Detecting movement {Math.round(progress)}%
              </p>
              {error && <p style={{ color: 'var(--kamari-cream)', marginTop: 8, textAlign: 'center' }}>{error}</p>}
            </>
          ) : (
            <div className="kamari-center" style={{ marginTop: 48 }}>
              <IonIcon icon={checkmarkCircle} style={{ fontSize: 76, color: 'var(--kamari-gold)' }} />
              <h1 style={{ color: 'var(--kamari-cream)' }}>Presence confirmed</h1>
              <p style={{ color: 'rgba(246,239,226,.85)', maxWidth: 300, margin: '8px auto 0' }}>
                Thank you. A real, present person was confirmed.
              </p>
              <IonButton className="kamari-btn" color="secondary" style={{ marginTop: 20 }} onClick={() => history.replace('/welcome')}>
                <IonIcon slot="start" icon={shieldCheckmark} /> Done
              </IonButton>
            </div>
          )}
          <span className="kamari-badge on-dark" style={{ marginTop: 18 }}>No video is stored</span>
        </div>
      </IonContent>
    </IonPage>
  );
}
