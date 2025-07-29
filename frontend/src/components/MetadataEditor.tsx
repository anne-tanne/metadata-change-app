import React, { useState, useEffect } from 'react';
import { PlusIcon, TrashIcon } from '@heroicons/react/24/outline';
import { ImageMetadata, MetadataSuggestion } from '../types';

interface MetadataEditorProps {
  metadata: ImageMetadata;
  suggestions: Record<string, MetadataSuggestion[]>;
}

const MetadataEditor: React.FC<MetadataEditorProps> = ({ metadata, suggestions }) => {
  const [localMetadata, setLocalMetadata] = useState<ImageMetadata>(metadata);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['File']));

  useEffect(() => {
    setLocalMetadata(metadata);
  }, [metadata]);

  const updateField = (section: string, field: string, value: unknown) => {
    setLocalMetadata(prev => ({
      ...prev,
      [section]: {
        ...(prev[section] as Record<string, unknown> || {}),
        [field]: value,
      },
    }));
  };

  const addField = (section: string) => {
    const fieldName = `NewField_${Date.now()}`;
    updateField(section, fieldName, '');
  };

  const removeField = (section: string, field: string) => {
    setLocalMetadata(prev => {
      const newSection = { ...(prev[section] as Record<string, unknown>) };
      delete newSection[field];
      return {
        ...prev,
        [section]: newSection,
      };
    });
  };

  const toggleSection = (section: string) => {
    setExpandedSections(prev => {
      const newSet = new Set(prev);
      if (newSet.has(section)) {
        newSet.delete(section);
      } else {
        newSet.add(section);
      }
      return newSet;
    });
  };

  const handleSuggestionClick = (section: string, field: string, value: string) => {
    updateField(section, field, value);
  };

  const renderField = (section: string, field: string, value: unknown) => {
    const fieldSuggestions = suggestions[field] || [];

    return (
      <div key={field} className="metadata-field">
        <div className="flex items-center justify-between">
          <label className="metadata-field-label">{field}</label>
          <button
            onClick={() => removeField(section, field)}
            className="text-error-500 hover:text-error-700 dark:text-error-400 dark:hover:text-error-300"
            title="Remove field"
          >
            <TrashIcon className="w-4 h-4" />
          </button>
        </div>
        <input
          type="text"
          value={String(value)}
          onChange={(e) => updateField(section, field, e.target.value)}
          className="metadata-field-input"
          placeholder={`Enter ${field.toLowerCase()}`}
        />
        {fieldSuggestions.length > 0 && (
          <div className="metadata-field-suggestions">
            {fieldSuggestions.slice(0, 3).map((suggestion, index) => (
              <button
                key={index}
                onClick={() => handleSuggestionClick(section, field, suggestion.value)}
                className="metadata-suggestion"
              >
                <span>{suggestion.value}</span>
                <span className="metadata-suggestion-count">{suggestion.count}</span>
              </button>
            ))}
          </div>
        )}
      </div>
    );
  };

  const renderSection = (section: string, data: unknown) => {
    const isExpanded = expandedSections.has(section);
    const fields = Object.entries(data as Record<string, unknown>);

    return (
      <div key={section} className="card p-6 mb-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">{section}</h3>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => addField(section)}
              className="btn-ghost p-1"
              title="Add field"
            >
              <PlusIcon className="w-4 h-4" />
            </button>
            <button
              onClick={() => toggleSection(section)}
              className="btn-ghost p-1"
              title={isExpanded ? 'Collapse' : 'Expand'}
            >
              {isExpanded ? '−' : '+'}
            </button>
          </div>
        </div>
        
        {isExpanded && (
          <div className="space-y-4">
            {fields.map(([field, value]) => renderField(section, field, value))}
          </div>
        )}
      </div>
    );
  };

  if (!localMetadata || Object.keys(localMetadata).length === 0) {
    return (
      <div className="card p-8 text-center">
        <p className="text-secondary-600 mb-4">No metadata available for this image.</p>
        <button
          onClick={() => addField('Custom')}
          className="btn-primary"
        >
          <PlusIcon className="w-4 h-4 mr-2" />
          Add Custom Field
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {Object.entries(localMetadata).map(([section, data]) => 
        renderSection(section, data)
      )}
      
      <button
        onClick={() => addField('Custom')}
        className="btn-secondary w-full"
      >
        <PlusIcon className="w-4 h-4 mr-2" />
        Add Custom Section
      </button>
    </div>
  );
};

export default MetadataEditor; 