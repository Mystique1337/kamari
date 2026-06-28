import React from 'react';
import { createRoot } from 'react-dom/client';
import { setupIonicReact } from '@ionic/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from './App';
import { KamariProvider } from './lib/state';

/* Ionic core CSS */
import '@ionic/react/css/core.css';
import '@ionic/react/css/normalize.css';
import '@ionic/react/css/structure.css';
import '@ionic/react/css/typography.css';
import '@ionic/react/css/padding.css';
import '@ionic/react/css/flex-utils.css';

/* Kámárí theme */
import './theme/variables.css';
import './theme/kamari.css';

setupIonicReact({ mode: 'ios' });

const queryClient = new QueryClient();

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <KamariProvider>
        <App />
      </KamariProvider>
    </QueryClientProvider>
  </React.StrictMode>,
);
