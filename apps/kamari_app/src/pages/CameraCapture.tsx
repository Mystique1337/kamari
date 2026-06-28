import {
  IonContent, IonPage, IonHeader, IonToolbar, IonTitle, IonButtons, IonBackButton,
  IonButton, IonIcon, IonSpinner,
} from '@ionic/react';
import { cameraOutline, refreshOutline } from 'ionicons/icons';
import { useEffect, useRef, useState } from 'react';
import { useHistory } from 'react-router-dom';
import { useKamari } from '../lib/state';
import { estimateAge } from '../lib/api';
import { captureFrame, captureNativeSelfie, isNative } from '../lib/camera';

export default function CameraCapture() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const history = useHistory();
  const { consentAccepted, setCapture } = useKamari();

  // Guard: must pass consent first.
  useEffect(() => {
    if (!consentAccepted) history.replace('/consent');
  }, [consentAccepted, history]);

  // Start the web camera stream (skipped on native — Capacitor opens its own camera).
  useEffect(() => {
    if (isNative()) return;
    let cancelled = false;
    (async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'user', width: { ideal: 720 }, height: { ideal: 720 } },
          audio: false,
        });
        if (cancelled) { stream.getTracks().forEach((t) => t.stop()); return; }
        streamRef.current = stream;
        if (videoRef.current) videoRef.current.srcObject = stream;
      } catch {
        setError('We couldn’t open the camera. Please allow camera access and try again.');
      }
    })();
    return () => {
      cancelled = true;
      streamRef.current?.getTracks().forEach((t) => t.stop());
    };
  }, []);

  const stopStream = () => streamRef.current?.getTracks().forEach((t) => t.stop());

  const run = async (dataUrl: string) => {
    setBusy(true);
    try {
      const result = await estimateAge(dataUrl, { language: 'en', country: 'NG' });
      setCapture(dataUrl, result);
      stopStream();
      history.push('/result');
    } catch {
      setError('Something went wrong reaching the age service. Please try again.');
    } finally {
      setBusy(false);
    }
  };

  const onCapture = async () => {
    if (busy) return;
    if (isNative()) {
      const dataUrl = await captureNativeSelfie();
      if (dataUrl) await run(dataUrl);
      return;
    }
    if (videoRef.current && videoRef.current.readyState >= 2) {
      await run(captureFrame(videoRef.current));
    }
  };

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonButtons slot="start"><IonBackButton defaultHref="/consent" /></IonButtons>
          <IonTitle>Take your selfie</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent className="kamari-hero kamari-pattern">
        <div className="kamari-pad" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', minHeight: '100%' }}>
          <p style={{ color: 'rgba(246,239,226,.85)', textAlign: 'center', maxWidth: 300 }}>
            Face the camera in good light. Your photo is checked once and never saved.
          </p>

          <div style={{
            width: 280, height: 280, borderRadius: '50%', overflow: 'hidden',
            border: '4px solid var(--kamari-gold)', boxShadow: 'var(--kamari-shadow)',
            margin: '20px 0', background: '#0d1830', position: 'relative',
          }}>
            {!isNative() && (
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                style={{ width: '100%', height: '100%', objectFit: 'cover', transform: 'scaleX(-1)' }}
              />
            )}
            {(busy) && (
              <div style={{
                position: 'absolute', inset: 0, display: 'grid', placeItems: 'center',
                background: 'rgba(13,24,48,.55)',
              }}>
                <IonSpinner name="crescent" style={{ color: 'var(--kamari-gold)' }} />
              </div>
            )}
          </div>

          {error && (
            <div className="kamari-card" style={{ padding: 14, marginBottom: 12, color: 'var(--kamari-ink)' }}>
              {error}
            </div>
          )}

          <IonButton className="kamari-btn" color="secondary" onClick={onCapture} disabled={busy}>
            <IonIcon slot="start" icon={busy ? refreshOutline : cameraOutline} />
            {busy ? 'Checking…' : 'Capture & check age'}
          </IonButton>
          <span className="kamari-badge on-dark" style={{ marginTop: 16 }}>📷 Photo never stored</span>
        </div>
      </IonContent>
    </IonPage>
  );
}
