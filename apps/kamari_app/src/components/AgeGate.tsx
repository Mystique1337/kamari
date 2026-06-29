import { IonButton, IonIcon, IonSpinner } from '@ionic/react';
import { cameraOutline, cloudUploadOutline } from 'ionicons/icons';
import { useEffect, useRef, useState } from 'react';
import { estimateAge } from '../lib/api';
import { captureFrame, captureNativeSelfie, isNative } from '../lib/camera';
import type { AgeEstimateResponse } from '../lib/types';

/** Inline age check (camera + upload) used by the demo integrations. */
export default function AgeGate({ onResult }: { onResult: (r: AgeEstimateResponse) => void }) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isNative()) return;
    let cancelled = false;
    (async () => {
      try {
        const s = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' }, audio: false });
        if (cancelled) { s.getTracks().forEach((t) => t.stop()); return; }
        streamRef.current = s;
        if (videoRef.current) videoRef.current.srcObject = s;
      } catch {
        setError('Allow camera access, or upload a photo instead.');
      }
    })();
    return () => { cancelled = true; streamRef.current?.getTracks().forEach((t) => t.stop()); };
  }, []);

  const run = async (dataUrl: string) => {
    setBusy(true);
    try {
      const r = await estimateAge(dataUrl, { language: 'en', country: 'NG' });
      streamRef.current?.getTracks().forEach((t) => t.stop());
      onResult(r);
    } catch {
      setError('Could not reach the age service. Please try again.');
    } finally { setBusy(false); }
  };

  const capture = async () => {
    if (busy) return;
    if (isNative()) { const d = await captureNativeSelfie(); if (d) await run(d); return; }
    if (videoRef.current && videoRef.current.readyState >= 2) await run(captureFrame(videoRef.current));
  };

  const onFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (!f) return;
    const rd = new FileReader();
    rd.onload = () => run(String(rd.result));
    rd.readAsDataURL(f);
    e.target.value = '';
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <div style={{
        width: 220, height: 220, borderRadius: '50%', overflow: 'hidden',
        border: '4px solid var(--kamari-gold)', background: '#0d1830', position: 'relative',
      }}>
        {!isNative() && (
          <video ref={videoRef} autoPlay playsInline muted
            style={{ width: '100%', height: '100%', objectFit: 'cover', transform: 'scaleX(-1)' }} />
        )}
        {busy && (
          <div style={{ position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', background: 'rgba(13,24,48,.55)' }}>
            <IonSpinner name="crescent" style={{ color: 'var(--kamari-gold)' }} />
          </div>
        )}
      </div>
      {error && <p className="kamari-muted" style={{ marginTop: 10, textAlign: 'center' }}>{error}</p>}
      <input ref={fileRef} type="file" accept="image/*" hidden onChange={onFile} />
      <div style={{ display: 'flex', gap: 10, marginTop: 14, flexWrap: 'wrap', justifyContent: 'center' }}>
        <IonButton className="kamari-btn" color="secondary" disabled={busy} onClick={capture}>
          <IonIcon slot="start" icon={cameraOutline} /> {busy ? 'Checking' : 'Verify with a selfie'}
        </IonButton>
        <IonButton fill="outline" disabled={busy} onClick={() => fileRef.current?.click()}>
          <IonIcon slot="start" icon={cloudUploadOutline} /> Upload a photo
        </IonButton>
      </div>
      <p className="kamari-muted" style={{ marginTop: 12, fontSize: '.78rem', textAlign: 'center' }}>
        Powered by Kamari. Your photo is processed once and never stored.
      </p>
    </div>
  );
}
