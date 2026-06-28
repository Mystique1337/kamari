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
    photo_never_stored: 'Photo never stored',
    estimate_note: 'An estimate, not a legal determination.',
    take_selfie: 'Take your selfie',
    capture: 'Capture and check age',
    checking: 'Checking',
    continue: 'Continue',
    language: 'Language',
    country: 'Country',
  },
  pcm: {
    tagline: 'A age check wey respect you, tuned for African face and skin. We no dey keep your photo.',
    begin: 'Start age check',
    photo_never_stored: 'We no dey keep photo',
    estimate_note: 'Na estimate, no be legal judgement.',
    take_selfie: 'Snap your selfie',
    capture: 'Snap and check age',
    checking: 'Dey check',
    continue: 'Continue',
    language: 'Language',
    country: 'Country',
  },
  fr: {
    tagline: "Une vérification d'âge respectueuse, adaptée aux visages et teints africains. Votre photo n'est jamais conservée.",
    begin: "Commencer la vérification",
    photo_never_stored: 'Photo jamais conservée',
    estimate_note: "Une estimation, pas une détermination légale.",
    take_selfie: 'Prenez votre selfie',
    capture: "Capturer et vérifier l'âge",
    checking: 'Vérification',
    continue: 'Continuer',
    language: 'Langue',
    country: 'Pays',
  },
  sw: {
    tagline: 'Ukaguzi wa umri wenye heshima, uliolenga nyuso na rangi za ngozi za Kiafrika. Picha yako haihifadhiwi kamwe.',
    begin: 'Anza ukaguzi wa umri',
    photo_never_stored: 'Picha haihifadhiwi',
    estimate_note: 'Ni makadirio, si uamuzi wa kisheria.',
    take_selfie: 'Piga selfie yako',
    capture: 'Piga na ukague umri',
    checking: 'Inakagua',
    continue: 'Endelea',
    language: 'Lugha',
    country: 'Nchi',
  },
};

export function t(lang: string, key: string): string {
  return STRINGS[lang]?.[key] ?? STRINGS.en[key] ?? key;
}
