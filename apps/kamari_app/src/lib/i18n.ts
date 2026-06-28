// Lightweight localisation for the consumer flow.
//
// The picker drives two things:
//   1. the `language` sent to the gateway, so Gemma writes the decision message in that
//      language (the model is genuinely multilingual);
//   2. a small set of UI strings translated here, with a graceful fallback to English
//      for any string or language not yet translated.
//
// Pan-African set. Native names are shown in the picker.
export interface Language {
  code: string;
  label: string;   // English label
  native: string;  // endonym
}

export const LANGUAGES: Language[] = [
  { code: 'en', label: 'English', native: 'English' },
  { code: 'pcm', label: 'Nigerian Pidgin', native: 'Naijá' },
  { code: 'fr', label: 'French', native: 'Français' },
  { code: 'sw', label: 'Swahili', native: 'Kiswahili' },
  { code: 'yo', label: 'Yoruba', native: 'Yorùbá' },
  { code: 'ha', label: 'Hausa', native: 'Hausa' },
  { code: 'ig', label: 'Igbo', native: 'Igbo' },
  { code: 'zu', label: 'Zulu', native: 'isiZulu' },
  { code: 'am', label: 'Amharic', native: 'አማርኛ' },
];

// Countries (legal threshold context passed to the gateway).
export interface Country { code: string; name: string; flag: string }
export const COUNTRIES: Country[] = [
  { code: 'NG', name: 'Nigeria', flag: '🇳🇬' },
  { code: 'GH', name: 'Ghana', flag: '🇬🇭' },
  { code: 'KE', name: 'Kenya', flag: '🇰🇪' },
  { code: 'ZA', name: 'South Africa', flag: '🇿🇦' },
  { code: 'ET', name: 'Ethiopia', flag: '🇪🇹' },
  { code: 'TZ', name: 'Tanzania', flag: '🇹🇿' },
  { code: 'CI', name: "Côte d'Ivoire", flag: '🇨🇮' },
  { code: 'SN', name: 'Senegal', flag: '🇸🇳' },
];

type Dict = Record<string, string>;

// English is the complete base. Other languages override the strings we are confident
// about; anything missing falls back to English automatically.
const STRINGS: Record<string, Dict> = {
  en: {
    tagline: 'A respectful age check, tuned for African faces and skin tones. Your photo is never stored.',
    begin: 'Begin age check',
    verify_cta: 'Verify your age',
    for_developers: 'For developers',
    pricing: 'Pricing',
    docs: 'Docs',
    photo_never_stored: 'Photo never stored',
    estimate_note: 'An estimate, not a legal determination.',
    take_selfie: 'Take your selfie',
    capture: 'Capture and check age',
    checking: 'Checking',
    continue: 'Continue',
    language: 'Language',
    country: 'Country',
    how_title: 'How it works',
    how_1: 'Take a quick selfie in good light.',
    how_2: 'Kamari estimates your age on a calibrated model.',
    how_3: 'Get a clear decision. Your photo is never stored.',
    feat_privacy: 'Privacy first',
    feat_privacy_d: 'Your photo is processed once and deleted. No image is kept.',
    feat_african: 'Built for Africa',
    feat_african_d: 'Trained and tested across African faces and skin tones.',
    feat_fast: 'Fast and multilingual',
    feat_fast_d: 'A decision in a moment, explained in your language.',
    hold_still: 'Hold still, centre your face',
    auto_capturing: 'Capturing',
  },
  pcm: {
    tagline: 'A age check wey respect you, tuned for African face and skin. We no dey keep your photo.',
    begin: 'Start age check',
    verify_cta: 'Check your age',
    for_developers: 'For developers',
    photo_never_stored: 'We no dey keep photo',
    estimate_note: 'Na estimate, no be legal judgement.',
    take_selfie: 'Snap your selfie',
    capture: 'Snap and check age',
    checking: 'Dey check',
    how_title: 'How e dey work',
    how_1: 'Snap quick selfie for better light.',
    how_2: 'Kamari go estimate your age with correct model.',
    how_3: 'You go see clear decision. We no dey keep your photo.',
    hold_still: 'Hold still, put your face for center',
  },
  fr: {
    tagline: "Une vérification d'âge respectueuse, adaptée aux visages et teints africains. Votre photo n'est jamais conservée.",
    begin: "Commencer la vérification",
    verify_cta: "Vérifier votre âge",
    for_developers: "Pour les développeurs",
    pricing: 'Tarifs',
    docs: 'Docs',
    photo_never_stored: 'Photo jamais conservée',
    estimate_note: "Une estimation, pas une détermination légale.",
    take_selfie: 'Prenez votre selfie',
    capture: "Capturer et vérifier l'âge",
    checking: 'Vérification',
    language: 'Langue',
    country: 'Pays',
    how_title: 'Comment ça marche',
    how_1: 'Prenez un selfie dans une bonne lumière.',
    how_2: "Kamari estime votre âge avec un modèle calibré.",
    how_3: "Obtenez une décision claire. Votre photo n'est jamais conservée.",
    hold_still: 'Ne bougez pas, centrez votre visage',
  },
  sw: {
    tagline: 'Ukaguzi wa umri wenye heshima, uliolenga nyuso na rangi za ngozi za Kiafrika. Picha yako haihifadhiwi kamwe.',
    begin: 'Anza ukaguzi wa umri',
    verify_cta: 'Thibitisha umri wako',
    for_developers: 'Kwa wasanidi',
    photo_never_stored: 'Picha haihifadhiwi',
    estimate_note: 'Ni makadirio, si uamuzi wa kisheria.',
    take_selfie: 'Piga selfie yako',
    capture: 'Piga na ukague umri',
    checking: 'Inakagua',
    language: 'Lugha',
    country: 'Nchi',
    how_title: 'Jinsi inavyofanya kazi',
    how_1: 'Piga selfie kwenye mwanga mzuri.',
    how_2: 'Kamari hukadiria umri wako kwa modeli sahihi.',
    how_3: 'Pata uamuzi wazi. Picha yako haihifadhiwi.',
    hold_still: 'Tulia, weka uso wako katikati',
  },
  yo: {
    tagline: 'Ayewo ojo-ori pelu owo, ti a se fun oju ati awo ara Afirika. A ki i fi foto re pamo.',
    begin: 'Bere ayewo ojo-ori',
    verify_cta: 'Se ayewo ojo-ori re',
    for_developers: 'Fun awon olupile',
    photo_never_stored: 'A ki i fi foto pamo',
    take_selfie: 'Ya selfie re',
    capture: 'Ya ki o si yewo ojo-ori',
    how_title: 'Bi o se n sise',
  },
};

export function t(lang: string, key: string): string {
  return STRINGS[lang]?.[key] ?? STRINGS.en[key] ?? key;
}
