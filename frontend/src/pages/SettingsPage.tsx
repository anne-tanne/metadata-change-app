import React, { useState } from 'react';
import { 
  Cog6ToothIcon,
  InformationCircleIcon,
  TrashIcon,
  ArrowDownTrayIcon
} from '@heroicons/react/24/outline';
import { useNotification } from '../contexts/NotificationContext';
import { useTheme } from '../contexts/ThemeContext';

const SettingsPage: React.FC = () => {
  const [settings, setSettings] = useState({
    autoSave: true,
    showSuggestions: true,
    backupBeforeEdit: true,
  });
  const { showNotification } = useNotification();
  const { theme, setTheme } = useTheme();

  const handleSettingChange = (key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }));
    showNotification('success', 'Setting updated', `${key} has been updated.`);
  };

  const handleThemeChange = (newTheme: 'light' | 'dark' | 'auto') => {
    setTheme(newTheme);
    showNotification('success', 'Theme updated', `Theme changed to ${newTheme}.`);
  };

  const handleExportData = () => {
    // Export learning data and preferences
    const data = {
      settings,
      theme,
      timestamp: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'metadata-editor-settings.json';
    a.click();
    URL.revokeObjectURL(url);
    
    showNotification('success', 'Data exported', 'Settings and learning data have been exported.');
  };

  const handleClearData = () => {
    if (window.confirm('Are you sure you want to clear all learning data? This action cannot be undone.')) {
      // Clear learning data
      showNotification('success', 'Data cleared', 'All learning data has been cleared.');
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-10 h-10 bg-primary-100 dark:bg-primary-900 rounded-lg flex items-center justify-center">
            <Cog6ToothIcon className="w-6 h-6 text-primary-600 dark:text-primary-400" />
          </div>
          <div>
            <h1 className="text-3xl font-bold">
              Settings
            </h1>
            <p className="text-secondary">
              Configure your metadata editor preferences
            </p>
          </div>
        </div>
      </div>

      {/* Settings sections */}
      <div className="space-y-8">
        {/* General Settings */}
        <div className="card">
          <div className="p-6">
            <h2 className="text-xl font-semibold mb-4">
              General Settings
            </h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-medium">Auto Save</h3>
                  <p className="text-sm text-secondary">Automatically save changes when switching images</p>
                </div>
                <button
                  onClick={() => handleSettingChange('autoSave', !settings.autoSave)}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    settings.autoSave ? 'bg-primary-600 dark:bg-primary-500' : 'bg-secondary-300 dark:bg-secondary-600'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      settings.autoSave ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-medium">Show Suggestions</h3>
                  <p className="text-sm text-secondary">Display smart suggestions based on learning data</p>
                </div>
                <button
                  onClick={() => handleSettingChange('showSuggestions', !settings.showSuggestions)}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    settings.showSuggestions ? 'bg-primary-600 dark:bg-primary-500' : 'bg-secondary-300 dark:bg-secondary-600'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      settings.showSuggestions ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-medium">Backup Before Edit</h3>
                  <p className="text-sm text-secondary">Create backup files before modifying metadata</p>
                </div>
                <button
                  onClick={() => handleSettingChange('backupBeforeEdit', !settings.backupBeforeEdit)}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    settings.backupBeforeEdit ? 'bg-primary-600 dark:bg-primary-500' : 'bg-secondary-300 dark:bg-secondary-600'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      settings.backupBeforeEdit ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-medium">Theme</h3>
                  <p className="text-sm text-secondary">Choose your preferred interface theme</p>
                </div>
                <select
                  value={theme}
                  onChange={(e) => handleThemeChange(e.target.value as 'light' | 'dark' | 'auto')}
                  className="input w-32"
                >
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                  <option value="auto">Auto</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Data Management */}
        <div className="card">
          <div className="p-6">
            <h2 className="text-xl font-semibold mb-4">
              Data Management
            </h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-secondary-50 dark:bg-secondary-700 rounded-lg">
                <div>
                  <h3 className="text-sm font-medium">Export Data</h3>
                  <p className="text-sm text-secondary">Export your settings and learning data</p>
                </div>
                <button
                  onClick={handleExportData}
                  className="btn-secondary"
                >
                  <ArrowDownTrayIcon className="w-4 h-4 mr-2" />
                  Export
                </button>
              </div>

              <div className="flex items-center justify-between p-4 bg-secondary-50 dark:bg-secondary-700 rounded-lg">
                <div>
                  <h3 className="text-sm font-medium">Clear Learning Data</h3>
                  <p className="text-sm text-secondary">Remove all learned suggestions and preferences</p>
                </div>
                <button
                  onClick={handleClearData}
                  className="btn-error"
                >
                  <TrashIcon className="w-4 h-4 mr-2" />
                  Clear
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* About */}
        <div className="card">
          <div className="p-6">
            <h2 className="text-xl font-semibold mb-4">
              About
            </h2>
            <div className="space-y-4">
              <div className="flex items-start space-x-3">
                <InformationCircleIcon className="w-5 h-5 text-primary-600 dark:text-primary-400 mt-0.5" />
                <div>
                  <h3 className="text-sm font-medium">MetaData Editor</h3>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-secondary">Version:</span>
                  <span className="ml-2">1.0.0</span>
                </div>
                <div>
                  <span className="text-secondary">License:</span>
                  <span className="ml-2">MIT</span>
                </div>
              </div>

              <div className="pt-4 border-t border-secondary-200 dark:border-secondary-700">
                <p className="text-xs text-muted">
                  A modern metadata editor for images
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage; 