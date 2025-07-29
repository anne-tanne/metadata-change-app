import React, { createContext, useContext, useReducer, ReactNode } from 'react';
import { ImageMetadata, MetadataSuggestion } from '../types';

interface MetadataState {
  metadata: ImageMetadata;
  suggestions: Record<string, MetadataSuggestion[]>;
  isLoading: boolean;
  error: string | null;
  learningData: Record<string, MetadataSuggestion[]>;
}

type MetadataAction =
  | { type: 'SET_METADATA'; payload: ImageMetadata }
  | { type: 'SET_SUGGESTIONS'; payload: Record<string, MetadataSuggestion[]> }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_LEARNING_DATA'; payload: Record<string, MetadataSuggestion[]> }
  | { type: 'UPDATE_METADATA_FIELD'; payload: { section: string; field: string; value: unknown } };

const initialState: MetadataState = {
  metadata: {},
  suggestions: {},
  isLoading: false,
  error: null,
  learningData: {},
};

function metadataReducer(state: MetadataState, action: MetadataAction): MetadataState {
  switch (action.type) {
    case 'SET_METADATA':
      return {
        ...state,
        metadata: action.payload,
        isLoading: false,
        error: null,
      };
    case 'SET_SUGGESTIONS':
      return {
        ...state,
        suggestions: action.payload,
      };
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      };
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
        isLoading: false,
      };
    case 'SET_LEARNING_DATA':
      return {
        ...state,
        learningData: action.payload,
      };
    case 'UPDATE_METADATA_FIELD':
      return {
        ...state,
        metadata: {
          ...state.metadata,
          [action.payload.section]: {
            ...(state.metadata[action.payload.section] as Record<string, unknown> || {}),
            [action.payload.field]: action.payload.value,
          },
        },
      };
    default:
      return state;
  }
}

interface MetadataContextType {
  state: MetadataState;
  dispatch: React.Dispatch<MetadataAction>;
  loadImageMetadata: (imagePath: string) => Promise<void>;
  updateMetadata: (imagePath: string, metadata: ImageMetadata) => Promise<boolean>;
  saveMetadata: (imagePath: string) => Promise<boolean>;
  getSuggestions: (fieldName: string) => Promise<MetadataSuggestion[]>;
}

const MetadataContext = createContext<MetadataContextType | undefined>(undefined);

export function MetadataProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(metadataReducer, initialState);

  const loadImageMetadata = async (imagePath: string) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      dispatch({ type: 'SET_ERROR', payload: null });

      const encodedPath = imagePath.replace(/\//g, '|');
      const response = await fetch(`/api/metadata/${encodedPath}`);
      
      if (!response.ok) {
        throw new Error(`Failed to load metadata: ${response.statusText}`);
      }

      const data = await response.json();
      dispatch({ type: 'SET_METADATA', payload: data.metadata });
      dispatch({ type: 'SET_SUGGESTIONS', payload: data.suggestions });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error instanceof Error ? error.message : 'Unknown error' });
    }
  };

  const updateMetadata = async (imagePath: string, metadata: ImageMetadata): Promise<boolean> => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      
      const encodedPath = imagePath.replace(/\//g, '|');
      const response = await fetch(`/api/metadata/${encodedPath}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ metadata }),
      });

      if (!response.ok) {
        throw new Error(`Failed to update metadata: ${response.statusText}`);
      }

      const result = await response.json();
      dispatch({ type: 'SET_LOADING', payload: false });
      return result.success;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error instanceof Error ? error.message : 'Unknown error' });
      dispatch({ type: 'SET_LOADING', payload: false });
      return false;
    }
  };

  const saveMetadata = async (imagePath: string): Promise<boolean> => {
    if (!state.metadata) {
      return false;
    }
    return await updateMetadata(imagePath, state.metadata);
  };

  const getSuggestions = async (fieldName: string): Promise<MetadataSuggestion[]> => {
    try {
      const response = await fetch(`/api/suggestions?field=${encodeURIComponent(fieldName)}`);
      if (!response.ok) {
        return [];
      }
      const data = await response.json();
      return data.suggestions || [];
    } catch (error) {
      return [];
    }
  };

  const value: MetadataContextType = {
    state,
    dispatch,
    loadImageMetadata,
    updateMetadata,
    saveMetadata,
    getSuggestions,
  };

  return (
    <MetadataContext.Provider value={value}>
      {children}
    </MetadataContext.Provider>
  );
}

export function useMetadata() {
  const context = useContext(MetadataContext);
  if (context === undefined) {
    throw new Error('useMetadata must be used within a MetadataProvider');
  }
  return context;
}