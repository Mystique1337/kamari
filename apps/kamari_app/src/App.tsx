import { IonApp, IonRouterOutlet } from '@ionic/react';
import { IonReactRouter } from '@ionic/react-router';
import { Route, Redirect } from 'react-router-dom';

import Welcome from './pages/Welcome';
import Consent from './pages/Consent';
import CameraCapture from './pages/CameraCapture';
import AgeResult from './pages/AgeResult';
import SecondaryCheck from './pages/SecondaryCheck';
import GuardianConsent from './pages/GuardianConsent';
import Login from './pages/Login';
import Pricing from './pages/Pricing';
import DeveloperDashboard from './pages/DeveloperDashboard';
import ApiKeys from './pages/ApiKeys';
import UsageLogs from './pages/UsageLogs';

export default function App() {
  return (
    <IonApp>
      <IonReactRouter>
        <IonRouterOutlet>
          <Route exact path="/welcome" component={Welcome} />
          <Route exact path="/consent" component={Consent} />
          <Route exact path="/capture" component={CameraCapture} />
          <Route exact path="/result" component={AgeResult} />
          <Route exact path="/secondary" component={SecondaryCheck} />
          <Route exact path="/guardian" component={GuardianConsent} />
          <Route exact path="/login" component={Login} />
          <Route exact path="/pricing" component={Pricing} />
          <Route exact path="/developer" component={DeveloperDashboard} />
          <Route exact path="/developer/keys" component={ApiKeys} />
          <Route exact path="/developer/usage" component={UsageLogs} />
          <Route exact path="/">
            <Redirect to="/welcome" />
          </Route>
        </IonRouterOutlet>
      </IonReactRouter>
    </IonApp>
  );
}
