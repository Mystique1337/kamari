// Demo integrations: mock third-party apps that gate entry with the Kamari API.
// Each shows the same pattern: ask for an age check, then allow or restrict.
import { footballOutline, moonOutline, wineOutline } from 'ionicons/icons';

export interface Demo {
  kind: string;
  name: string;
  tagline: string;
  accent: string;     // brand colour for the mock app
  gate: string;       // why a check is required
  allowed: string;    // content shown when allowed in
  icon: string;       // imported ionicon
}

export const DEMOS: Record<string, Demo> = {
  betting: {
    kind: 'betting',
    name: 'BetLagos',
    tagline: 'Sports betting and live odds',
    accent: '#1e7a46',
    gate: 'You must be 18 or older to place a bet.',
    allowed: 'You are in. Today\'s top fixtures and live odds are ready.',
    icon: footballOutline,
  },
  adult: {
    kind: 'adult',
    name: 'After Dark',
    tagline: 'Adults-only content',
    accent: '#7a1e5a',
    gate: 'This area is for adults only. Verify you are 18 or older to continue.',
    allowed: 'Access granted. Please enjoy responsibly.',
    icon: moonOutline,
  },
  liquor: {
    kind: 'liquor',
    name: 'The Cellar',
    tagline: 'Fine wines and spirits',
    accent: '#8a4b1e',
    gate: 'You must be 18 or older to shop alcohol.',
    allowed: 'Cheers. Browse our wines and spirits.',
    icon: wineOutline,
  },
};

export const DEMO_LIST = Object.values(DEMOS);
