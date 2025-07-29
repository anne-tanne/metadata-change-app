import React, { createContext, useContext, useReducer, ReactNode } from 'react';
import { ImageData, FolderStats } from '../types';

interface FolderState {
  selectedFolder: string | null;
  images: ImageData[];
  isLoading: boolean;
  error: string | null;
  stats: FolderStats | null;
}

type FolderAction =
  | { type: 'SET_FOLDER'; payload: string }
  | { type: 'SET_IMAGES'; payload: ImageData[] }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_STATS'; payload: FolderStats }
  | { type: 'UPDATE_IMAGE'; payload: { path: string; metadata: ImageData['metadata'] } }
  | { type: 'CLEAR_FOLDER' };

const initialState: FolderState = {
  selectedFolder: null,
  images: [],
  isLoading: false,
  error: null,
  stats: null,
};

function folderReducer(state: FolderState, action: FolderAction): FolderState {
  switch (action.type) {
    case 'SET_FOLDER':
      return {
        ...state,
        selectedFolder: action.payload,
        error: null,
      };
    case 'SET_IMAGES':
      return {
        ...state,
        images: action.payload,
        isLoading: false,
        error: null,
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
    case 'SET_STATS':
      return {
        ...state,
        stats: action.payload,
      };
    case 'UPDATE_IMAGE':
      return {
        ...state,
        images: state.images.map(img =>
          img.path === action.payload.path
            ? { ...img, metadata: action.payload.metadata }
            : img
        ),
      };
    case 'CLEAR_FOLDER':
      return {
        ...initialState,
      };
    default:
      return state;
  }
}

interface FolderContextType {
  state: FolderState;
  dispatch: React.Dispatch<FolderAction>;
  selectFolder: (folderPath: string) => Promise<void>;
  scanFolder: (folderPath: string) => Promise<void>;
  updateImageMetadata: (imagePath: string, metadata: ImageData['metadata']) => void;
  clearFolder: () => void;
}

const FolderContext = createContext<FolderContextType | undefined>(undefined);

export function FolderProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(folderReducer, initialState);

  const selectFolder = async (folderPath: string) => {
    dispatch({ type: 'SET_FOLDER', payload: folderPath });
    await scanFolder(folderPath);
  };

  const scanFolder = async (folderPath: string) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      dispatch({ type: 'SET_ERROR', payload: null });

      const response = await fetch('/api/folder/scan', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ folder_path: folderPath }),
      });

      if (!response.ok) {
        throw new Error(`Failed to scan folder: ${response.statusText}`);
      }

      const data = await response.json();
      dispatch({ type: 'SET_IMAGES', payload: data.images });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error instanceof Error ? error.message : 'Unknown error' });
    }
  };

  const updateImageMetadata = (imagePath: string, metadata: ImageData['metadata']) => {
    dispatch({ type: 'UPDATE_IMAGE', payload: { path: imagePath, metadata } });
  };

  const clearFolder = () => {
    dispatch({ type: 'CLEAR_FOLDER' });
  };

  const value: FolderContextType = {
    state,
    dispatch,
    selectFolder,
    scanFolder,
    updateImageMetadata,
    clearFolder,
  };

  return (
    <FolderContext.Provider value={value}>
      {children}
    </FolderContext.Provider>
  );
}

export function useFolder() {
  const context = useContext(FolderContext);
  if (context === undefined) {
    throw new Error('useFolder must be used within a FolderProvider');
  }
  return context;
} 