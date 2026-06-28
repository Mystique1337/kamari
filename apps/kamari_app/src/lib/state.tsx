import { createContext, useContext, useState, type ReactNode } from 'react';
import type { AgeEstimateResponse } from './types';

// Lightweight app-flow state: consent + the most recent capture/result.
// Deliberately in-memory (and never persisting the image) to match the privacy posture.
interface KamariState {
  consentAccepted: boolean;
  acceptConsent: () => void;
  lastImage: string | null;
  lastResult: AgeEstimateResponse | null;
  setCapture: (img: string, result: AgeEstimateResponse) => void;
  reset: () => void;
}

const Ctx = createContext<KamariState | null>(null);

export function KamariProvider({ children }: { children: ReactNode }) {
  const [consentAccepted, setConsent] = useState(false);
  const [lastImage, setLastImage] = useState<string | null>(null);
  const [lastResult, setLastResult] = useState<AgeEstimateResponse | null>(null);

  const value: KamariState = {
    consentAccepted,
    acceptConsent: () => setConsent(true),
    lastImage,
    lastResult,
    setCapture: (img, result) => {
      setLastImage(img);
      setLastResult(result);
    },
    reset: () => {
      setLastImage(null);
      setLastResult(null);
    },
  };
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useKamari(): KamariState {
  const v = useContext(Ctx);
  if (!v) throw new Error('useKamari must be used within KamariProvider');
  return v;
}
