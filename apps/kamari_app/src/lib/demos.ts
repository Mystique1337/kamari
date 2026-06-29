// Demo integrations: mock third-party apps that gate entry with the Kamari API.
// Each shows the same pattern: ask for an age check, then allow or restrict.
import { footballOutline, moonOutline, wineOutline } from 'ionicons/icons';

export interface DemoItem { img: string; title: string; meta: string }
export interface Demo {
  kind: string;
  name: string;
  tagline: string;
  accent: string;     // brand colour for the mock app
  gate: string;       // why a check is required
  allowed: string;    // content shown when allowed in
  icon: string;       // imported ionicon
  hero: string;       // hero image
  items: DemoItem[];  // realistic content tiles shown once allowed in
}

// Topical placeholder photos (loremflickr). The tiles also have an accent fallback,
// so the layout stays intentional even if an image is slow.
const img = (tags: string, lock: number, w = 320, h = 200) =>
  `https://loremflickr.com/${w}/${h}/${tags}?lock=${lock}`;

export const DEMOS: Record<string, Demo> = {
  betting: {
    kind: 'betting',
    name: 'BetLagos',
    tagline: 'Sports betting and live odds',
    accent: '#1e7a46',
    gate: 'You must be 18 or older to place a bet.',
    allowed: 'You are in. Today\'s top fixtures and live odds are ready.',
    icon: footballOutline,
    hero: img('football,stadium', 21, 720, 280),
    items: [
      { img: img('soccer', 22), title: 'Eagles vs Lions', meta: '1.85   3.20   4.50' },
      { img: img('basketball', 23), title: 'Sharks vs Hawks', meta: '2.10   3.00   3.40' },
      { img: img('boxing', 24), title: 'Title Fight', meta: '1.55   -   2.45' },
    ],
  },
  adult: {
    kind: 'adult',
    name: 'After Dark',
    tagline: 'Adults-only content',
    accent: '#7a1e5a',
    gate: 'This area is for adults only. Verify you are 18 or older to continue.',
    allowed: 'Access granted. Please enjoy responsibly.',
    icon: moonOutline,
    hero: img('nightclub,neon', 31, 720, 280),
    items: [
      { img: img('cocktail', 32), title: 'The Lounge', meta: 'Members only' },
      { img: img('party', 33), title: 'Live Sessions', meta: '18+' },
      { img: img('dance', 34), title: 'After Hours', meta: 'Tonight' },
    ],
  },
  liquor: {
    kind: 'liquor',
    name: 'The Cellar',
    tagline: 'Fine wines and spirits',
    accent: '#8a4b1e',
    gate: 'You must be 18 or older to shop alcohol.',
    allowed: 'Cheers. Browse our wines and spirits.',
    icon: wineOutline,
    hero: img('wine,cellar', 41, 720, 280),
    items: [
      { img: img('wine', 42), title: 'Cabernet Sauvignon', meta: 'N18,500' },
      { img: img('whiskey', 43), title: 'Single Malt 12yr', meta: 'N42,000' },
      { img: img('champagne', 44), title: 'Brut Champagne', meta: 'N31,200' },
    ],
  },
};

export const DEMO_LIST = Object.values(DEMOS);
