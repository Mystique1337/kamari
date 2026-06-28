import { IonApp, IonRouterOutlet, IonSpinner } from '@ionic/react';
import { IonReactRouter } from '@ionic/react-router';
import { Route, Redirect } from 'react-router-dom';
import { Suspense, lazy } from 'react';

// Welcome (the landing) loads eagerly for a fast first paint; the rest are code-split.
import Welcome from './pages/Welcome';

const Consent = lazy(() => import('./pages/Consent'));
const CameraCapture = lazy(() => import('./pages/CameraCapture'));
const AgeResult = lazy(() => import('./pages/AgeResult'));
const SecondaryCheck = lazy(() => import('./pages/SecondaryCheck'));
const GuardianConsent = lazy(() => import('./pages/GuardianConsent'));
const Login = lazy(() => import('./pages/Login'));
const Pricing = lazy(() => import('./pages/Pricing'));
const Docs = lazy(() => import('./pages/Docs'));
const DeveloperDashboard = lazy(() => import('./pages/DeveloperDashboard'));
const ApiKeys = lazy(() => import('./pages/ApiKeys'));
const UsageLogs = lazy(() => import('./pages/UsageLogs'));

function Loading() {
  return (
    <div style={{ display: 'grid', placeItems: 'center', height: '100%' }}>
      <IonSpinner name="crescent" />
    </div>
  );
}

export default function App() {
  return (
    <IonApp>
      <IonReactRouter>
        <Suspense fallback={<Loading />}>
          <IonRouterOutlet>
            <Route exact path="/welcome" component={Welcome} />
            <Route exact path="/consent" component={Consent} />
            <Route exact path="/capture" component={CameraCapture} />
            <Route exact path="/result" component={AgeResult} />
            <Route exact path="/secondary" component={SecondaryCheck} />
            <Route exact path="/guardian" component={GuardianConsent} />
            <Route exact path="/login" component={Login} />
            <Route exact path="/pricing" component={Pricing} />
            <Route exact path="/docs" component={Docs} />
            <Route exact path="/developer" component={DeveloperDashboard} />
            <Route exact path="/developer/keys" component={ApiKeys} />
            <Route exact path="/developer/usage" component={UsageLogs} />
            <Route exact path="/">
              <Redirect to="/welcome" />
            </Route>
          </IonRouterOutlet>
        </Suspense>
      </IonReactRouter>
    </IonApp>
  );
}
