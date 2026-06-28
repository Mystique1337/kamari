import { Capacitor } from '@capacitor/core';

/** Native (Capacitor) selfie capture. Returns a data URL or null. */
export async function captureNativeSelfie(): Promise<string | null> {
  if (!Capacitor.isNativePlatform()) return null;
  const { Camera, CameraResultType, CameraSource, CameraDirection } = await import('@capacitor/camera');
  const photo = await Camera.getPhoto({
    quality: 85,
    resultType: CameraResultType.DataUrl,
    source: CameraSource.Camera,
    direction: CameraDirection.Front,
    allowEditing: false,
    saveToGallery: false, // privacy: never persist the selfie
  });
  return photo.dataUrl ?? null;
}

export const isNative = () => Capacitor.isNativePlatform();

/** Grab a still frame from a running <video> stream as a JPEG data URL. */
export function captureFrame(video: HTMLVideoElement, maxSize = 640): string {
  const scale = Math.min(1, maxSize / Math.max(video.videoWidth, video.videoHeight));
  const w = Math.round(video.videoWidth * scale);
  const h = Math.round(video.videoHeight * scale);
  const canvas = document.createElement('canvas');
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext('2d')!;
  // mirror so the selfie matches what the user sees
  ctx.translate(w, 0);
  ctx.scale(-1, 1);
  ctx.drawImage(video, 0, 0, w, h);
  return canvas.toDataURL('image/jpeg', 0.9);
}
