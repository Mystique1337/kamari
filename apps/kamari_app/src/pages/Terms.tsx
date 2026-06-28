import {
  IonContent, IonPage, IonHeader, IonToolbar, IonTitle, IonButtons, IonBackButton,
} from '@ionic/react';

export default function Terms() {
  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonButtons slot="start"><IonBackButton defaultHref="/welcome" /></IonButtons>
          <IonTitle>Terms</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent className="kamari-bg kamari-pad">
        <div style={{ maxWidth: 720, margin: '0 auto' }}>
          <h2>Terms of service</h2>

          <h3>The service</h3>
          <p>Kamari estimates age from a face image and returns a decision and explanation. It is an
          estimate to support an age-assurance flow, not a legal age determination, and must not be
          the sole basis for a legal eligibility decision.</p>

          <h3>Acceptable use</h3>
          <p>Do not use Kamari for unlawful purposes, to harm minors, or for 1:N face search or
          surveillance. You must obtain consent from the people you verify and comply with the laws
          that apply to you.</p>

          <h3>Plans and limits</h3>
          <p>API access is offered in tiers with per-minute rate limits and monthly quotas. Exceeding
          a limit returns HTTP 429. We may change limits with notice.</p>

          <h3>Open source</h3>
          <p>The Kamari code is open source under Apache-2.0. You may self-host it under that license.
          These terms govern use of the managed API, which is provided as is, without warranty, and
          our liability is limited to the amount you paid in the prior month.</p>

          <h3>Contact</h3>
          <p>Questions: team@catalyzu.io.</p>
        </div>
      </IonContent>
    </IonPage>
  );
}
