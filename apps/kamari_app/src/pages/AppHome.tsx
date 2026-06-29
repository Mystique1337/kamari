import {
  IonContent, IonPage, IonButton, IonIcon, IonSelect, IonSelectOption,
} from '@ionic/react';
import { arrowForward, codeSlashOutline } from 'ionicons/icons';
import { type CSSProperties } from 'react';
import { useHistory } from 'react-router-dom';
import KamariMark from '../components/KamariMark';
import { useKamari } from '../lib/state';
import { LANGUAGES, t } from '../lib/i18n';

// Plain entry for the installed app. No marketing sections; straight to the age check.
// The web build shows the full marketing homepage (Welcome) instead.
export default function AppHome() {
  const history = useHistory();
  const { language, setLanguage } = useKamari();
  const tr = (k: string) => t(language, k);

  return (
    <IonPage>
      <IonContent fullscreen>
        <div className="kamari-hero kamari-pattern" style={{ minHeight: '100%', display: 'flex', flexDirection: 'column' }}>
          <div style={{ position: 'absolute', top: 12, right: 12, zIndex: 5 }}>
            <IonSelect
              aria-label="Language" value={language} interface="popover"
              onIonChange={(e) => setLanguage(e.detail.value)}
              style={{ color: 'var(--kamari-cream)', maxWidth: 150 }}
            >
              {LANGUAGES.map((l) => (
                <IonSelectOption key={l.code} value={l.code}>{l.native}</IonSelectOption>
              ))}
            </IonSelect>
          </div>

          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', textAlign: 'center', padding: '32px 24px' }}>
            <KamariMark size={96} tone="gold" />
            <h1 style={{ fontSize: '2.8rem', margin: '18px 0 0', color: 'var(--kamari-cream)' }}>Kámárí</h1>
            <p style={{ maxWidth: 320, margin: '14px auto 0', color: 'rgba(246,239,226,.86)', lineHeight: 1.55 }}>
              {tr('tagline')}
            </p>
            <span className="kamari-badge on-dark" style={{ marginTop: 18 }}>📷 {tr('photo_never_stored')}</span>
          </div>

          <div className="kamari-pad kamari-stack" style={{ paddingBottom: 32 }}>
            <div className="kamari-kente" />
            <IonButton expand="block" className="kamari-btn" color="secondary" onClick={() => history.push('/consent')}>
              {tr('verify_cta')}
              <IonIcon slot="end" icon={arrowForward} />
            </IonButton>
            <IonButton
              expand="block" fill="clear"
              style={{ '--color': 'var(--kamari-cream)' } as CSSProperties}
              onClick={() => history.push('/login')}
            >
              <IonIcon slot="start" icon={codeSlashOutline} /> {tr('for_developers')}
            </IonButton>
            <p style={{ color: 'rgba(246,239,226,.6)', textAlign: 'center', fontSize: '.78rem' }}>{tr('estimate_note')}</p>
          </div>
        </div>
      </IonContent>
    </IonPage>
  );
}
