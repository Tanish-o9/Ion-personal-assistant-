import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from './store/queryClient';
import { AssistantProvider } from './contexts/AssistantContext';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <AssistantProvider>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </AssistantProvider>
    </QueryClientProvider>
  </React.StrictMode>
);
