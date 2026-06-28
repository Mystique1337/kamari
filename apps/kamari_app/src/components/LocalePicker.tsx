import { IonItem, IonLabel, IonSelect, IonSelectOption } from '@ionic/react';
import { useKamari } from '../lib/state';
import { LANGUAGES, COUNTRIES, t } from '../lib/i18n';

/** Language + country pickers. Language drives the in-language decision message. */
export default function LocalePicker() {
  const { language, country, setLanguage, setCountry } = useKamari();
  return (
    <div className="kamari-card" style={{ padding: 6 }}>
      <IonItem lines="full">
        <IonLabel>{t(language, 'language')}</IonLabel>
        <IonSelect
          value={language}
          interface="action-sheet"
          onIonChange={(e) => setLanguage(e.detail.value)}
        >
          {LANGUAGES.map((l) => (
            <IonSelectOption key={l.code} value={l.code}>
              {l.native} ({l.label})
            </IonSelectOption>
          ))}
        </IonSelect>
      </IonItem>
      <IonItem lines="none">
        <IonLabel>{t(language, 'country')}</IonLabel>
        <IonSelect
          value={country}
          interface="action-sheet"
          onIonChange={(e) => setCountry(e.detail.value)}
        >
          {COUNTRIES.map((c) => (
            <IonSelectOption key={c.code} value={c.code}>
              {c.flag} {c.name}
            </IonSelectOption>
          ))}
        </IonSelect>
      </IonItem>
    </div>
  );
}
