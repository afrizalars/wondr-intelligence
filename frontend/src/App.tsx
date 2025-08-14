import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

import AuthLayout from './layouts/AuthLayout';
import DashboardLayout from './layouts/DashboardLayoutApple';
import LoginApple from './pages/LoginApple';
import RegisterApple from './pages/RegisterApple';
import Playground from './pages/PlaygroundApple';
import Merchants from './pages/Merchants';
import Guardrails from './pages/Guardrails';
import PromptTemplates from './pages/PromptTemplates';
import ApiKeys from './pages/ApiKeys';
import SearchHistory from './pages/SearchHistory';
import GlobalKnowledge from './pages/GlobalKnowledge';
import { AuthProvider } from './contexts/AuthContext';
import appleTheme from './theme/appleTheme';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={appleTheme}>
        <CssBaseline />
        <Router>
          <AuthProvider>
            <Routes>
              <Route path="/auth" element={<AuthLayout />}>
                <Route path="login" element={<LoginApple />} />
                <Route path="register" element={<RegisterApple />} />
              </Route>
              <Route path="/" element={<DashboardLayout />}>
                <Route index element={<Navigate to="/playground" replace />} />
                <Route path="playground" element={<Playground />} />
                <Route path="merchants" element={<Merchants />} />
                <Route path="guardrails" element={<Guardrails />} />
                <Route path="prompts" element={<PromptTemplates />} />
                <Route path="api-keys" element={<ApiKeys />} />
                <Route path="history" element={<SearchHistory />} />
                <Route path="knowledge" element={<GlobalKnowledge />} />
              </Route>
            </Routes>
          </AuthProvider>
        </Router>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;