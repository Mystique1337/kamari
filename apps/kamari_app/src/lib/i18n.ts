// Lightweight localisation for the consumer flow.
//
// The picker drives two things:
//   1. the `language` sent to the gateway, so Gemma writes the decision message in that
//      language (the model is genuinely multilingual);
//   2. the UI strings translated here, with a graceful fallback to English for any string
//      not yet translated for a language.
//
// Translations below cover the full consumer flow across the Pan-African set. They are
// AI-assisted and good for launch, but a final native-speaker review is recommended,
// especially for diacritics in Yoruba/Igbo and the Amharic script.
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

// English is the complete base. Each other language fully translates the consumer-flow
// strings; anything missing falls back to English automatically.
const STRINGS: Record<string, Dict> = {
  en: {
    tagline: 'A respectful age check, tuned for African faces and skin tones. Your photo is never stored.',
    verify_cta: 'Verify your age',
    take_selfie: 'Take your selfie',
    capture: 'Capture and check age',
    checking: 'Checking',
    hold_still: 'Hold still, centre your face',
    photo_never_stored: 'Photo never stored',
    continue: 'Continue',
    estimate_note: 'An estimate, not a legal determination.',
    language: 'Language',
    country: 'Country',
  },
  pcm: {
    tagline: 'A age check wey respect you, tuned for African face and skin. We no dey keep your photo.',
    verify_cta: 'Check your age',
    take_selfie: 'Snap your selfie',
    capture: 'Snap and check age',
    checking: 'Dey check',
    hold_still: 'Hold still, put your face for center',
    photo_never_stored: 'We no dey keep photo',
    continue: 'Continue',
    estimate_note: 'Na estimate, no be legal judgement.',
    language: 'Language',
    country: 'Country',
  },
  fr: {
    tagline: "Une vérification d'âge respectueuse, adaptée aux visages et teints africains. Votre photo n'est jamais conservée.",
    verify_cta: 'Vérifier votre âge',
    take_selfie: 'Prenez votre selfie',
    capture: "Capturer et vérifier l'âge",
    checking: 'Vérification',
    hold_still: 'Ne bougez pas, centrez votre visage',
    photo_never_stored: 'Photo jamais conservée',
    continue: 'Continuer',
    estimate_note: 'Une estimation, pas une détermination légale.',
    language: 'Langue',
    country: 'Pays',
  },
  sw: {
    tagline: 'Ukaguzi wa umri wenye heshima, uliolenga nyuso na rangi za ngozi za Kiafrika. Picha yako haihifadhiwi kamwe.',
    verify_cta: 'Thibitisha umri wako',
    take_selfie: 'Piga selfie yako',
    capture: 'Piga na ukague umri',
    checking: 'Inakagua',
    hold_still: 'Tulia, weka uso wako katikati',
    photo_never_stored: 'Picha haihifadhiwi',
    continue: 'Endelea',
    estimate_note: 'Ni makadirio, si uamuzi wa kisheria.',
    language: 'Lugha',
    country: 'Nchi',
  },
  yo: {
    tagline: 'Àyẹ̀wò ọjọ́-orí pẹ̀lú ọ̀wọ̀, tí a ṣe fún ojú àti àwọ̀ ara Áfríkà. A kì í pa fọtò rẹ mọ́.',
    verify_cta: 'Ṣàyẹ̀wò ọjọ́-orí rẹ',
    take_selfie: 'Ya fọtò ara rẹ',
    capture: 'Ya fọtò kí o sì ṣàyẹ̀wò ọjọ́-orí',
    checking: 'Ń ṣàyẹ̀wò',
    hold_still: 'Dúró jẹ́ẹ́, mú ojú rẹ wà ní àárín',
    photo_never_stored: 'A kì í pa fọtò mọ́',
    continue: 'Tẹ̀síwájú',
    estimate_note: 'Ìfojúsùn ni, kì í ṣe ìdájọ́ òfin.',
    language: 'Èdè',
    country: 'Orílẹ̀-èdè',
  },
  ha: {
    tagline: 'Binciken shekaru mai mutuntawa, wanda aka tsara don fuskoki da launin fata na Afirka. Ba a taɓa ajiye hotonka.',
    verify_cta: 'Tabbatar da shekarunka',
    take_selfie: 'Ɗauki hoton kanka',
    capture: 'Ɗauki hoto a duba shekaru',
    checking: 'Ana dubawa',
    hold_still: 'Kar ka motsa, ka kawo fuskarka tsakiya',
    photo_never_stored: 'Ba a ajiye hoto',
    continue: 'Ci gaba',
    estimate_note: 'Ƙiyasi ne, ba hukuncin doka ba.',
    language: 'Harshe',
    country: 'Ƙasa',
  },
  ig: {
    tagline: 'Nyocha afọ nke na-akwanyere mmadụ ùgwù, e mere maka ihu na agba akpụkpọ ahụ ndị Africa. Anaghị echekwa foto gị.',
    verify_cta: 'Nyochaa afọ gị',
    take_selfie: 'Sere foto gị',
    capture: 'Sere foto ma nyochaa afọ',
    checking: 'Na-enyocha',
    hold_still: "Guzoro chịm, debe ihu gị n'etiti",
    photo_never_stored: 'Anaghị echekwa foto',
    continue: "Gaa n'ihu",
    estimate_note: 'Ọ bụ atụmatụ, ọ bụghị mkpebi iwu.',
    language: 'Asụsụ',
    country: 'Obodo',
  },
  zu: {
    tagline: 'Ukuhlolwa kweminyaka okunenhlonipho, kulungiselelwe ubuso nemibala yesikhumba yase-Afrika. Isithombe sakho asigcinwa.',
    verify_cta: 'Qinisekisa iminyaka yakho',
    take_selfie: 'Thatha isithombe sakho',
    capture: 'Thatha bese uhlola iminyaka',
    checking: 'Iyahlola',
    hold_still: 'Ima ndawonye, beka ubuso bakho maphakathi',
    photo_never_stored: 'Isithombe asigcinwa',
    continue: 'Qhubeka',
    estimate_note: 'Yisilinganiso, hhayi isinqumo somthetho.',
    language: 'Ulimi',
    country: 'Izwe',
  },
  am: {
    tagline: 'ለአፍሪካ ፊቶችና የቆዳ ቀለሞች የተስተካከለ አክብሮት ያለው የዕድሜ ማረጋገጫ። ፎቶዎ ፈጽሞ አይቀመጥም።',
    verify_cta: 'ዕድሜዎን ያረጋግጡ',
    take_selfie: 'የራስዎን ፎቶ ያንሱ',
    capture: 'ፎቶ አንስተው ዕድሜን ያረጋግጡ',
    checking: 'በማረጋገጥ ላይ',
    hold_still: 'ቀጥ ብለው ይቁሙ፣ ፊትዎን መሃል ያድርጉ',
    photo_never_stored: 'ፎቶ አይቀመጥም',
    continue: 'ይቀጥሉ',
    estimate_note: 'ግምት ነው፣ ሕጋዊ ውሳኔ አይደለም።',
    language: 'ቋንቋ',
    country: 'ሀገር',
  },
};

export function t(lang: string, key: string): string {
  return STRINGS[lang]?.[key] ?? STRINGS.en[key] ?? key;
}
