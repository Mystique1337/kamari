import {
  IonContent, IonPage, IonButton, IonIcon, IonSelect, IonSelectOption,
} from '@ionic/react';
import {
  arrowForward, codeSlashOutline, eyeOffOutline, globeOutline, flashOutline, languageOutline,
} from 'ionicons/icons';
import { useHistory } from 'react-router-dom';
import KamariMark from '../components/KamariMark';
import { useKamari } from '../lib/state';
import { LANGUAGES, t } from '../lib/i18n';

export default function Welcome() {
  const history = useHistory();
  const { language, setLanguage } = useKamari();
  const tr = (k: string) => t(language, k);

  const features = [
    { icon: eyeOffOutline, title: tr('feat_privacy'), body: tr('feat_privacy_d') },
    { icon: globeOutline, title: tr('feat_african'), body: tr('feat_african_d') },
    { icon: flashOutline, title: tr('feat_fast'), body: tr('feat_fast_d') },
  ];
  const steps = [tr('how_1'), tr('how_2'), tr('how_3')];

  return (
    <IonPage>
      <IonContent fullscreen>
        {/* Language switch */}
        <div style={{ position: 'absolute', top: 12, right: 12, zIndex: 5 }}>
          <IonSelect
            aria-label="Language"
            value={language}
            interface="popover"
            onIonChange={(e) => setLanguage(e.detail.value)}
            style={{ color: 'var(--kamari-cream)', maxWidth: 150 }}
          >
            {LANGUAGES.map((l) => (
              <IonSelectOption key={l.code} value={l.code}>{l.native}</IonSelectOption>
            ))}
          </IonSelect>
        </div>

        <div className="kamari-hero kamari-pattern" style={{ minHeight: '58vh', padding: '28px' }}>
          <div style={{ paddingTop: 36, display: 'flex', justifyContent: 'center' }}>
            <KamariMark size={88} tone="gold" />
          </div>
          <div className="kamari-center" style={{ marginTop: 22 }}>
            <p className="kamari-eyebrow"><IonIcon icon={languageOutline} /> African age verification</p>
            <h1 style={{ fontSize: '3rem', margin: '8px 0 0', color: 'var(--kamari-cream)' }}>Kámárí</h1>
            <p style={{ maxWidth: 340, margin: '14px auto 0', color: 'rgba(246,239,226,.88)', lineHeight: 1.55 }}>
              {tr('tagline')}
            </p>
            <span className="kamari-badge on-dark" style={{ marginTop: 16 }}>📷 {tr('photo_never_stored')}</span>
          </div>
        </div>

        <div className="kamari-pad kamari-stack">
          <div className="kamari-kente" />
          <IonButton expand="block" className="kamari-btn" color="secondary" onClick={() => history.push('/consent')}>
            {tr('verify_cta')}
            <IonIcon slot="end" icon={arrowForward} />
          </IonButton>

          {/* How it works */}
          <h2 style={{ margin: '12px 4px 0' }}>{tr('how_title')}</h2>
          <div className="kamari-stack">
            {steps.map((s, i) => (
              <div key={i} className="kamari-card" style={{ padding: 16, display: 'flex', gap: 14, alignItems: 'center' }}>
                <div style={{
                  width: 34, height: 34, flexShrink: 0, borderRadius: '50%', display: 'grid', placeItems: 'center',
                  background: 'var(--kamari-gold)', color: 'var(--kamari-indigo-deep)', fontWeight: 700,
                }}>{i + 1}</div>
                <span style={{ fontSize: '.95rem' }}>{s}</span>
              </div>
            ))}
          </div>

          {/* Feature cards */}
          <div className="kamari-stack" style={{ marginTop: 6 }}>
            {features.map((f) => (
              <div key={f.title} className="kamari-card" style={{ padding: 18, display: 'flex', gap: 14 }}>
                <IonIcon icon={f.icon} style={{ fontSize: 26, color: 'var(--kamari-indigo)', flexShrink: 0 }} />
                <div>
                  <strong>{f.title}</strong>
                  <p className="kamari-muted" style={{ margin: '4px 0 0', fontSize: '.9rem' }}>{f.body}</p>
                </div>
              </div>
            ))}
          </div>

          <IonButton expand="block" fill="outline" color="primary" onClick={() => history.push('/login')}>
            <IonIcon slot="start" icon={codeSlashOutline} />
            {tr('for_developers')}
          </IonButton>
          <div style={{ display: 'flex', gap: 8 }}>
            <IonButton fill="clear" size="small" color="medium" style={{ flex: 1 }} onClick={() => history.push('/docs')}>{tr('docs')}</IonButton>
            <IonButton fill="clear" size="small" color="medium" style={{ flex: 1 }} onClick={() => history.push('/pricing')}>{tr('pricing')}</IonButton>
          </div>
          <p className="kamari-muted kamari-center" style={{ fontSize: '.76rem' }}>
            {tr('estimate_note')} Open source under Apache 2.0.
          </p>
        </div>
      </IonContent>
    </IonPage>
  );
}
