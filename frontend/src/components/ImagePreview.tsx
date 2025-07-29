import React, { useState } from 'react';

interface ImageData {
  path: string;
  filename: string;
  metadata: any;
  size: number;
  modified: string;
}

interface ImagePreviewProps {
  image: ImageData;
}

const ImagePreview: React.FC<ImagePreviewProps> = ({ image }) => {
  const [imageError, setImageError] = useState(false);

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="space-y-4">
      {/* Image display */}
      <div className="image-preview aspect-video">
        {!imageError ? (
          <img
            src={`file://${image.path}`}
            alt={image.filename}
            className="w-full h-full object-contain"
            onError={() => setImageError(true)}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-secondary-100 rounded-lg">
            <div className="text-center">
              <div className="w-16 h-16 bg-secondary-200 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-secondary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <p className="text-secondary-600 text-sm">Image preview not available</p>
            </div>
          </div>
        )}
      </div>

      {/* Image info */}
      <div className="card p-4">
        <h3 className="text-lg font-semibold text-secondary-900 mb-3">
          Image Information
        </h3>
        <div className="space-y-3">
          <div className="flex justify-between">
            <span className="text-sm text-secondary-600">Filename:</span>
            <span className="text-sm font-medium text-secondary-900 truncate ml-2">
              {image.filename}
            </span>
          </div>
          
          <div className="flex justify-between">
            <span className="text-sm text-secondary-600">Size:</span>
            <span className="text-sm font-medium text-secondary-900">
              {formatFileSize(image.size)}
            </span>
          </div>
          
          <div className="flex justify-between">
            <span className="text-sm text-secondary-600">Modified:</span>
            <span className="text-sm font-medium text-secondary-900">
              {formatDate(image.modified)}
            </span>
          </div>
          
          {image.metadata?.File && (
            <>
              {image.metadata.File.ImageWidth && image.metadata.File.ImageHeight && (
                <div className="flex justify-between">
                  <span className="text-sm text-secondary-600">Dimensions:</span>
                  <span className="text-sm font-medium text-secondary-900">
                    {image.metadata.File.ImageWidth} × {image.metadata.File.ImageHeight}
                  </span>
                </div>
              )}
              
              {image.metadata.File.Format && (
                <div className="flex justify-between">
                  <span className="text-sm text-secondary-600">Format:</span>
                  <span className="text-sm font-medium text-secondary-900">
                    {image.metadata.File.Format}
                  </span>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Quick metadata summary */}
      {image.metadata && Object.keys(image.metadata).length > 0 && (
        <div className="card p-4">
          <h3 className="text-lg font-semibold text-secondary-900 mb-3">
            Metadata Summary
          </h3>
          <div className="space-y-2">
            {Object.entries(image.metadata).map(([section, data]) => {
              if (typeof data === 'object' && data !== null) {
                const fieldCount = Object.keys(data).length;
                return (
                  <div key={section} className="flex justify-between items-center">
                    <span className="text-sm text-secondary-600 capitalize">
                      {section.toLowerCase()}:
                    </span>
                    <span className="text-sm font-medium text-secondary-900">
                      {fieldCount} field{fieldCount !== 1 ? 's' : ''}
                    </span>
                  </div>
                );
              }
              return null;
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default ImagePreview; 