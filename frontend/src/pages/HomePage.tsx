import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FolderOpenIcon,
  PhotoIcon,
  ArrowRightIcon,
  FolderIcon
} from '@heroicons/react/24/outline';
import { useFolder } from '../contexts/FolderContext';
import { useNotification } from '../contexts/NotificationContext';

const HomePage: React.FC = () => {
  const [selectedFolder, setSelectedFolder] = useState<string>('');
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [selectionMode, setSelectionMode] = useState<'folder' | 'files'>('folder');
  const filesInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();
  const { selectFolder, state } = useFolder();
  const { showNotification } = useNotification();

  const handleFolderSelect = async () => {
    if (!selectedFolder.trim() && selectedFiles.length === 0) {
      showNotification('warning', 'No selection', 'Please select a folder or images.');
      return;
    }

    try {
      if (selectionMode === 'folder' && selectedFolder.trim()) {
        await selectFolder(selectedFolder);
        showNotification('success', 'Folder loaded', `Successfully loaded ${state.images.length} images.`);
      } else if (selectionMode === 'files' && selectedFiles.length > 0) {
        // For individual files, we'll show a message for now
        showNotification('info', 'Files selected', `Successfully selected ${selectedFiles.length} images. Individual file handling will be implemented soon.`);
        return;
      }
      navigate('/editor');
    } catch (error) {
      showNotification('error', 'Error loading selection', error instanceof Error ? error.message : 'Unknown error');
    }
  };

  const handleFilesPickerClick = () => {
    setSelectionMode('files');
    filesInputRef.current?.click();
  };

  const handleFilesChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    setSelectedFiles(files);
  };

  return (
    <div className="max-w-7xl mx-auto">
      {/* Selection Options */}
      <div className="card max-w-2xl mx-auto mb-12">
        <div className="p-8">
          <div className="text-center mb-6">
            <FolderOpenIcon className="w-12 h-12 text-primary-500 mx-auto mb-4" />
            <h2 className="text-2xl font-semibold mb-2 font-display">
              Select Your Images
            </h2>
            <p className="text-secondary-700 dark:text-secondary-200">
              Choose a folder or select individual images
            </p>
          </div>

          {/* Selection Mode Tabs */}
          <div className="flex space-x-1 mb-6 bg-secondary-100 dark:bg-secondary-700 p-1 rounded-lg">
            <button
              onClick={() => setSelectionMode('folder')}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                selectionMode === 'folder'
                  ? 'bg-white dark:bg-secondary-800 shadow-sm'
                  : 'text-secondary-700 dark:text-secondary-200 hover:text-secondary-900 dark:hover:text-white'
              }`}
            >
              <FolderIcon className="w-4 h-4 inline mr-2" />
              Folder
            </button>
            <button
              onClick={() => setSelectionMode('files')}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                selectionMode === 'files'
                  ? 'bg-white dark:bg-secondary-800 shadow-sm'
                  : 'text-secondary-700 dark:text-secondary-200 hover:text-secondary-900 dark:hover:text-white'
              }`}
            >
              <PhotoIcon className="w-4 h-4 inline mr-2" />
              Individual Images
            </button>
          </div>

          {/* Folder Selection */}
          {selectionMode === 'folder' && (
            <div className="space-y-4">
              <div>
                <label className="metadata-field-label">
                  Folder Path
                </label>
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={selectedFolder}
                    onChange={(e) => setSelectedFolder(e.target.value)}
                    placeholder="/Users/username/Pictures or C:\Users\username\Pictures"
                    className="metadata-field-input flex-1"
                  />
                </div>

                <p className="text-sm text-secondary-600 dark:text-secondary-300 mt-2">
                  Enter the full path to your images folder (e.g., /Users/username/Pictures).
                </p>
              </div>
            </div>
          )}

          {/* Individual Files Selection */}
          {selectionMode === 'files' && (
            <div className="space-y-4">
              <div>
                <label className="metadata-field-label">
                  Select Images
                </label>
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={selectedFiles.length > 0 ? `${selectedFiles.length} images selected` : ''}
                    placeholder="No images selected"
                    className="metadata-field-input flex-1"
                    readOnly
                  />
                  <button
                    onClick={handleFilesPickerClick}
                    className="btn-secondary px-4"
                  >
                    Browse
                  </button>
                </div>
                <input
                  ref={filesInputRef}
                  type="file"
                  multiple
                  accept="image/*"
                  onChange={handleFilesChange}
                  className="hidden"
                />
              </div>
              
              {selectedFiles.length > 0 && (
                <div className="mt-4">
                  <h4 className="text-sm font-medium mb-2">Selected Images:</h4>
                  <div className="max-h-32 overflow-y-auto space-y-1">
                    {selectedFiles.map((file, index) => (
                      <div key={index} className="text-sm text-secondary-700 dark:text-secondary-200 bg-secondary-50 dark:bg-secondary-700 px-3 py-1 rounded">
                        {file.name}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          <button
            onClick={handleFolderSelect}
            disabled={(!selectedFolder.trim() && selectedFiles.length === 0) || state.isLoading}
            className="btn-primary w-full mt-6"
          >
            {state.isLoading ? (
              <>
                <div className="loading-spinner w-4 h-4 mr-2"></div>
                Loading Images...
              </>
            ) : (
              <>
                <FolderOpenIcon className="w-4 h-4 mr-2" />
                Load Images
                <ArrowRightIcon className="w-4 h-4 ml-2" />
              </>
            )}
          </button>

          {state.error && (
            <div className="mt-4 p-3 bg-error-50 dark:bg-error-900 border border-error-200 dark:border-error-700 rounded-lg">
              <p className="text-error-800 dark:text-error-200 text-sm">{state.error}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default HomePage; 