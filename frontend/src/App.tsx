import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { FolderProvider } from './contexts/FolderContext';
import { MetadataProvider } from './contexts/MetadataContext';
import { NotificationProvider } from './contexts/NotificationContext';
import { ThemeProvider } from './contexts/ThemeContext';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import EditorPage from './pages/EditorPage';
import SettingsPage from './pages/SettingsPage';
import './index.css';

function App() {
  return (
    <ThemeProvider>
      <Router>
        <NotificationProvider>
          <FolderProvider>
            <MetadataProvider>
              <div className="App min-h-screen gradient-bg">
                <Layout>
                  <Routes>
                    <Route path="/" element={<HomePage />} />
                    <Route path="/editor" element={<EditorPage />} />
                    <Route path="/settings" element={<SettingsPage />} />
                  </Routes>
                </Layout>
              </div>
            </MetadataProvider>
          </FolderProvider>
        </NotificationProvider>
      </Router>
    </ThemeProvider>
  );
}

export default App; 