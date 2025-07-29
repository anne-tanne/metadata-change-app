import React, { useState, useEffect } from 'react';
import { 
  ChevronLeftIcon, 
  ChevronRightIcon,
  CheckIcon
} from '@heroicons/react/24/outline';
import { useFolder } from '../contexts/FolderContext';
import { useMetadata } from '../contexts/MetadataContext';
import { useNotification } from '../contexts/NotificationContext';
import MetadataEditor from '../components/MetadataEditor';
import ImagePreview from '../components/ImagePreview';

const EditorPage: React.FC = () => {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const { state: folderState } = useFolder();
  const { state: metadataState, loadImageMetadata, saveMetadata } = useMetadata();
  const { showNotification } = useNotification();

  const currentImage = folderState.images[currentImageIndex];

  useEffect(() => {
    if (currentImage) {
      loadImageMetadata(currentImage.path);
    }
  }, [currentImage, loadImageMetadata]);

  const handlePrevious = () => {
    if (currentImageIndex > 0) {
      setCurrentImageIndex(currentImageIndex - 1);
    }
  };

  const handleNext = () => {
    if (currentImageIndex < folderState.images.length - 1) {
      setCurrentImageIndex(currentImageIndex + 1);
    }
  };

  const handleSave = async () => {
    if (!currentImage) return;

    try {
      const success = await saveMetadata(currentImage.path);
      if (success) {
        showNotification('success', 'Metadata saved', 'Image metadata has been updated successfully.');
      } else {
        showNotification('error', 'Save failed', 'Failed to save metadata. Please try again.');
      }
    } catch (error) {
      showNotification('error', 'Save error', error instanceof Error ? error.message : 'Unknown error');
    }
  };

  const handleSaveAndNext = async () => {
    await handleSave();
    if (currentImageIndex < folderState.images.length - 1) {
      setCurrentImageIndex(currentImageIndex + 1);
    }
  };

  if (!folderState.selectedFolder) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-semibold text-secondary-900 mb-4 font-display">
          No folder selected
        </h2>
        <p className="text-secondary-600 mb-6">
          Please select a folder containing images to start editing metadata.
        </p>
        <button
          onClick={() => window.history.back()}
          className="btn-primary"
        >
          Go Back
        </button>
      </div>
    );
  }

  if (folderState.images.length === 0) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-semibold text-secondary-900 mb-4 font-display">
          No images found
        </h2>
        <p className="text-secondary-600 mb-6">
          No supported image files were found in the selected folder.
        </p>
        <button
          onClick={() => window.history.back()}
          className="btn-primary"
        >
          Go Back
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-3xl font-bold text-secondary-900 font-display">
            Metadata Editor
          </h1>
          <div className="flex items-center space-x-4">
            <div className="text-sm text-secondary-600">
              {currentImageIndex + 1} of {folderState.images.length}
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={handlePrevious}
                disabled={currentImageIndex === 0}
                className="btn-secondary"
              >
                <ChevronLeftIcon className="w-4 h-4" />
              </button>
              <button
                onClick={handleNext}
                disabled={currentImageIndex === folderState.images.length - 1}
                className="btn-secondary"
              >
                <ChevronRightIcon className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Progress bar */}
        <div className="progress-bar">
          <div 
            className="progress-bar-fill"
            style={{ width: `${((currentImageIndex + 1) / folderState.images.length) * 100}%` }}
          />
        </div>
      </div>

      {/* Main content */}
      <div className="grid lg:grid-cols-2 gap-8">
        {/* Image preview */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-secondary-900 font-display">
            Image Preview
          </h2>
          {currentImage && (
            <ImagePreview image={currentImage} />
          )}
        </div>

        {/* Metadata editor */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-secondary-900 font-display">
              Metadata
            </h2>
            <div className="flex items-center space-x-2">
              <button
                onClick={handleSave}
                disabled={metadataState.isLoading}
                className="btn-success"
              >
                <CheckIcon className="w-4 h-4 mr-2" />
                Save
              </button>
              <button
                onClick={handleSaveAndNext}
                disabled={metadataState.isLoading || currentImageIndex === folderState.images.length - 1}
                className="btn-primary"
              >
                Save & Next
                <ChevronRightIcon className="w-4 h-4 ml-2" />
              </button>
            </div>
          </div>

          {metadataState.isLoading ? (
            <div className="card p-8 text-center">
              <div className="loading-spinner w-8 h-8 mx-auto mb-4"></div>
              <p className="text-secondary-600">Loading metadata...</p>
            </div>
          ) : metadataState.error ? (
            <div className="card p-6">
              <div className="p-4 bg-error-50 border border-error-200 rounded-lg">
                <p className="text-sm text-error-700">{metadataState.error}</p>
              </div>
            </div>
          ) : (
            <MetadataEditor 
              metadata={metadataState.metadata}
              suggestions={metadataState.suggestions}
            />
          )}
        </div>
      </div>

      {/* Image list */}
      <div className="mt-12">
        <h3 className="text-lg font-semibold text-secondary-900 mb-4">
          All Images ({folderState.images.length})
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {folderState.images.map((image, index) => (
            <button
              key={image.path}
              onClick={() => setCurrentImageIndex(index)}
              className={`card-hover p-3 text-left transition-all duration-200 ${
                index === currentImageIndex 
                  ? 'ring-2 ring-primary-500 bg-primary-50' 
                  : 'hover:bg-secondary-50'
              }`}
            >
              <div className="aspect-square bg-secondary-100 rounded-lg mb-2 overflow-hidden">
                <img
                  src={`file://${image.path}`}
                  alt={image.filename}
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    e.currentTarget.style.display = 'none';
                  }}
                />
              </div>
              <p className="text-xs text-secondary-600 truncate">
                {image.filename}
              </p>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default EditorPage; 