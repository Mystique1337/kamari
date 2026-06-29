import {
  IonContent, IonPage, IonHeader, IonToolbar, IonTitle, IonButtons, IonBackButton,
} from '@ionic/react';

export default function Privacy() {
  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonButtons slot="start"><IonBackButton defaultHref="/welcome" /></IonButtons>
          <IonTitle>Privacy</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent className="kamari-bg kamari-pad">
        <div style={{ maxWidth: 720, margin: '0 auto' }}>
          <h2>Privacy policy</h2>
          <p className="kamari-muted">Kamari is privacy-first by design. The short version: we check, we decide, we do not keep your photo.</p>

          <h3>What we process</h3>
          <p>When you run an age check, your selfie is sent to our model, processed in the moment to
          estimate age, and then discarded. The image is not written to disk or stored.</p>

          <h3>What we store</h3>
          <p>We store decision metadata only: the decision, reason code, model version, request id,
          and timestamps, plus API usage counts for billing and abuse prevention. We do not store
          images, and we do not create or store face embeddings by default. Optional 1:1
          verification embeddings, if ever enabled, are opt-in and scoped to a single subject; we
          never run 1:N face search.</p>

          <h3>Consent and children</h3>
          <p>We ask for explicit consent before any age check. Kamari produces an estimate, not a
          legal age determination, and is deliberately conservative near the age limit. Likely
          minors are routed to a guardian consent flow and are never enrolled for recognition.</p>

          <h3>Processors</h3>
          <p>We use Modal (model serving), Supabase (auth and metadata), Railway (hosting), and an
          email workflow (transactional email). We do not sell personal data.</p>

          <h3>Your rights</h3>
          <p>You can request access to or deletion of your account data. Contact us at
          chidi.ashinze@gmail.com.</p>

          <p className="kamari-muted" style={{ fontSize: '.85rem', marginTop: 24 }}>
            This is an estimate, not a legal age determination.
          </p>
        </div>
      </IonContent>
    </IonPage>
  );
}
