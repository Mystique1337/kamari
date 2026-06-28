import { IonApp, IonRouterOutlet } from '@ionic/react';
import { IonReactRouter } from '@ionic/react-router';
import { Route, Redirect } from 'react-router-dom';

import Welcome from './pages/Welcome';
import Consent from './pages/Consent';
import CameraCapture from './pages/CameraCapture';
import AgeResult from './pages/AgeResult';
import DeveloperDashboard from './pages/DeveloperDashboard';
import ApiKeys from './pages/ApiKeys';

export default function App() {
  return (
    <IonApp>
      <IonReactRouter>
        <IonRouterOutlet>
          <Route exact path="/welcome" component={Welcome} />
          <Route exact path="/consent" component={Consent} />
          <Route exact path="/capture" component={CameraCapture} />
          <Route exact path="/result" component={AgeResult} />
          <Route exact path="/developer" component={DeveloperDashboard} />
          <Route exact path="/developer/keys" component={ApiKeys} />
          <Route exact path="/">
            <Redirect to="/welcome" />
          </Route>
        </IonRouterOutlet>
      </IonReactRouter>
    </IonApp>
  );
}
