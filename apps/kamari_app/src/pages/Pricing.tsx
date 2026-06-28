import {
  IonContent, IonPage, IonHeader, IonToolbar, IonTitle, IonButtons, IonBackButton,
  IonButton, IonIcon, IonSpinner, IonBadge,
} from '@ionic/react';
import { checkmarkCircle, sparklesOutline } from 'ionicons/icons';
import { useHistory } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { listPlans, getPlan, setPlan } from '../lib/api';
import { useAuth } from '../lib/auth';

export default function Pricing() {
  const history = useHistory();
  const { session, getToken } = useAuth();
  const token = getToken();
  const qc = useQueryClient();

  const { data: plans, isLoading } = useQuery({ queryKey: ['plans'], queryFn: listPlans });
  const { data: current } = useQuery({
    queryKey: ['plan', token], queryFn: () => getPlan(token as string), enabled: Boolean(token),
  });

  const change = useMutation({
    mutationFn: (plan: string) => setPlan(token as string, plan),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['plan'] });
      qc.invalidateQueries({ queryKey: ['usage-summary'] });
    },
  });

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonButtons slot="start"><IonBackButton defaultHref="/welcome" /></IonButtons>
          <IonTitle>Pricing</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent className="kamari-bg kamari-pad">
        <p className="kamari-eyebrow" style={{ color: 'var(--kamari-terracotta)' }}>Kamari infrastructure</p>
        <h2 style={{ marginTop: 6 }}>Pay for what you verify</h2>
        <p className="kamari-muted" style={{ marginTop: 4 }}>
          Open source and self-hostable. Use our managed API and pick a plan that fits your volume.
          This is a demo: switching plans applies the limits instantly, with no payment.
        </p>

        {isLoading ? (
          <div style={{ textAlign: 'center', marginTop: 30 }}><IonSpinner name="crescent" /></div>
        ) : (
          <div className="kamari-stack" style={{ marginTop: 18 }}>
            {(plans ?? []).map((p) => {
              const active = current?.plan === p.key;
              return (
                <div key={p.key} className="kamari-card kamari-pad"
                  style={{ border: active ? '2px solid var(--kamari-gold)' : undefined }}>
                  <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between' }}>
                    <strong style={{ fontSize: '1.2rem' }}>{p.label}</strong>
                    {active && <IonBadge color="warning">Current</IonBadge>}
                  </div>
                  <div style={{ fontFamily: 'var(--kamari-font-display)', fontSize: '2rem', margin: '6px 0' }}>
                    {p.price_usd === 0 ? 'Free' : `$${p.price_usd}`}
                    {p.price_usd > 0 && <span style={{ fontSize: '.9rem', color: 'var(--kamari-muted)' }}> /month</span>}
                  </div>
                  <p className="kamari-muted" style={{ margin: '0 0 10px', fontSize: '.9rem' }}>{p.blurb}</p>
                  <div className="kamari-stack" style={{ gap: 6 }}>
                    {p.features.map((f) => (
                      <div key={f} style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                        <IonIcon icon={checkmarkCircle} style={{ color: 'var(--kamari-green)' }} />
                        <span style={{ fontSize: '.9rem' }}>{f}</span>
                      </div>
                    ))}
                  </div>
                  <div style={{ marginTop: 14 }}>
                    {!session ? (
                      <IonButton expand="block" className="kamari-btn" color="secondary"
                        onClick={() => history.push('/login')}>
                        Sign in to choose
                      </IonButton>
                    ) : active ? (
                      <IonButton expand="block" fill="outline" color="medium" disabled>
                        Your current plan
                      </IonButton>
                    ) : (
                      <IonButton expand="block" className="kamari-btn" color="secondary"
                        disabled={change.isPending} onClick={() => change.mutate(p.key)}>
                        {change.isPending ? <IonSpinner name="dots" /> : (
                          <>
                            <IonIcon slot="start" icon={sparklesOutline} />
                            Switch to {p.label} (demo)
                          </>
                        )}
                      </IonButton>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        <p className="kamari-muted kamari-center" style={{ fontSize: '.78rem', marginTop: 18 }}>
          Need more, or want to self-host? Kamari is open source under Apache 2.0.
        </p>
      </IonContent>
    </IonPage>
  );
}
