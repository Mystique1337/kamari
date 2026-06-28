import {
  IonContent, IonPage, IonHeader, IonToolbar, IonTitle, IonButtons, IonBackButton,
  IonButton, IonIcon, IonSpinner, IonToggle,
} from '@ionic/react';
import { cameraOutline, refreshOutline, checkmarkCircle, cloudUploadOutline } from 'ionicons/icons';
import { useEffect, useRef, useState } from 'react';
import { useHistory } from 'react-router-dom';
import { useKamari } from '../lib/state';
import { estimateAge } from '../lib/api';
import { captureFrame, captureNativeSelfie, isNative } from '../lib/camera';
import { t } from '../lib/i18n';

export default function CameraCapture() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [ready, setReady] = useState(false);   // face area looks well-lit + sharp
  const [count, setCount] = useState<number | null>(null); // countdown
  const [auto, setAuto] = useState(true);
  const history = useHistory();
  const { consentAccepted, setCapture, language, country } = useKamari();
  const tr = (k: string) => t(language, k);

  const busyRef = useRef(false);
  const streakRef = useRef(0);

  useEffect(() => {
    if (!consentAccepted) history.replace('/consent');
  }, [consentAccepted, history]);

  useEffect(() => {
    if (isNative()) return;
    let cancelled = false;
    (async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'user', width: { ideal: 720 }, height: { ideal: 720 } }, audio: false,
        });
        if (cancelled) { stream.getTracks().forEach((t) => t.stop()); return; }
        streamRef.current = stream;
        if (videoRef.current) videoRef.current.srcObject = stream;
      } catch {
        setError('We could not open the camera. Please allow camera access and try again.');
      }
    })();
    return () => { cancelled = true; streamRef.current?.getTracks().forEach((t) => t.stop()); };
  }, []);

  const stopStream = () => streamRef.current?.getTracks().forEach((t) => t.stop());

  const run = async (dataUrl: string) => {
    busyRef.current = true; setBusy(true);
    try {
      const result = await estimateAge(dataUrl, { language, country });
      setCapture(dataUrl, result);
      stopStream();
      history.push('/result');
    } catch {
      setError('Something went wrong reaching the age service. Please try again.');
    } finally {
      busyRef.current = false; setBusy(false);
    }
  };

  const onCapture = async () => {
    if (busyRef.current) return;
    if (isNative()) {
      const dataUrl = await captureNativeSelfie();
      if (dataUrl) await run(dataUrl);
      return;
    }
    if (videoRef.current && videoRef.current.readyState >= 2) await run(captureFrame(videoRef.current));
  };

  const fileRef = useRef<HTMLInputElement>(null);
  const onFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => { stopStream(); run(String(reader.result)); };
    reader.readAsDataURL(file);
    e.target.value = '';
  };

  // Readiness sampling: brightness + sharpness of the centre region. Drives auto-capture.
  useEffect(() => {
    if (isNative()) return;
    const id = setInterval(() => {
      const v = videoRef.current;
      if (!v || v.readyState < 2 || busyRef.current || count !== null) return;
      const n = 48;
      const c = document.createElement('canvas'); c.width = n; c.height = n;
      const ctx = c.getContext('2d'); if (!ctx) return;
      const s = Math.min(v.videoWidth, v.videoHeight) * 0.6;
      ctx.drawImage(v, (v.videoWidth - s) / 2, (v.videoHeight - s) / 2, s, s, 0, 0, n, n);
      const d = ctx.getImageData(0, 0, n, n).data;
      let sum = 0; const lum = new Float32Array(n * n);
      for (let i = 0; i < n * n; i++) {
        lum[i] = 0.299 * d[i * 4] + 0.587 * d[i * 4 + 1] + 0.114 * d[i * 4 + 2];
        sum += lum[i];
      }
      const bright = sum / (n * n);
      let sharp = 0;
      for (let i = 1; i < n * n; i++) sharp += Math.abs(lum[i] - lum[i - 1]);
      sharp /= n * n;
      const ok = bright > 45 && bright < 225 && sharp > 4.5;
      setReady(ok);
      streakRef.current = ok ? streakRef.current + 1 : 0;
      if (auto && streakRef.current >= 3) { streakRef.current = 0; beginCountdown(); }
    }, 400);
    return () => clearInterval(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [auto, count]);

  const beginCountdown = () => {
    if (busyRef.current || count !== null) return;
    let n = 3; setCount(n);
    const id = setInterval(() => {
      n -= 1;
      if (n <= 0) { clearInterval(id); setCount(null); onCapture(); }
      else setCount(n);
    }, 600);
  };

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonButtons slot="start"><IonBackButton defaultHref="/welcome" /></IonButtons>
          <IonTitle>{tr('take_selfie')}</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent>
        <div className="kamari-hero kamari-pattern kamari-pad" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', minHeight: '100%' }}>
          <p style={{ color: ready ? 'var(--kamari-gold)' : 'rgba(246,239,226,.85)', textAlign: 'center', maxWidth: 300, fontWeight: ready ? 600 : 400 }}>
            {ready ? '✓ Looking good' : tr('hold_still')}
          </p>

          <div style={{
            width: 280, height: 280, borderRadius: '50%', overflow: 'hidden',
            border: `4px solid ${ready ? 'var(--kamari-green)' : 'var(--kamari-gold)'}`,
            boxShadow: 'var(--kamari-shadow)', margin: '18px 0', background: '#0d1830', position: 'relative',
            transition: 'border-color .2s',
          }}>
            {!isNative() && (
              <video ref={videoRef} autoPlay playsInline muted
                style={{ width: '100%', height: '100%', objectFit: 'cover', transform: 'scaleX(-1)' }} />
            )}
            {/* Face guide oval */}
            <div style={{
              position: 'absolute', top: '14%', left: '24%', width: '52%', height: '72%',
              border: '2px dashed rgba(246,239,226,.5)', borderRadius: '50%', pointerEvents: 'none',
            }} />
            {count !== null && (
              <div style={{ position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', background: 'rgba(13,24,48,.45)' }}>
                <span style={{ fontSize: 80, fontWeight: 700, color: 'var(--kamari-cream)', fontFamily: 'var(--kamari-font-display)' }}>{count}</span>
              </div>
            )}
            {busy && (
              <div style={{ position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', background: 'rgba(13,24,48,.55)' }}>
                <IonSpinner name="crescent" style={{ color: 'var(--kamari-gold)' }} />
              </div>
            )}
          </div>

          {error && (
            <div className="kamari-card" style={{ padding: 14, marginBottom: 12, color: 'var(--kamari-ink)' }}>{error}</div>
          )}

          <IonButton className="kamari-btn" color="secondary" onClick={onCapture} disabled={busy}>
            <IonIcon slot="start" icon={busy ? refreshOutline : (ready ? checkmarkCircle : cameraOutline)} />
            {busy ? tr('checking') : tr('capture')}
          </IonButton>

          {/* Upload a photo instead (great on desktop) */}
          <input ref={fileRef} type="file" accept="image/*" hidden onChange={onFile} />
          <IonButton fill="clear" style={{ color: 'var(--kamari-cream)', marginTop: 4 }} onClick={() => fileRef.current?.click()} disabled={busy}>
            <IonIcon slot="start" icon={cloudUploadOutline} /> Upload a photo
          </IonButton>

          {!isNative() && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginTop: 6, color: 'rgba(246,239,226,.85)' }}>
              <IonToggle checked={auto} onIonChange={(e) => setAuto(e.detail.checked)} aria-label="Auto capture" />
              <span style={{ fontSize: '.85rem' }}>Auto capture</span>
            </div>
          )}
          <span className="kamari-badge on-dark" style={{ marginTop: 14 }}>📷 {tr('photo_never_stored')}</span>
        </div>
      </IonContent>
    </IonPage>
  );
}
