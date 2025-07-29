// Core data types
export interface ImageData {
  path: string;
  filename: string;
  metadata: ImageMetadata;
  size: number;
  modified: string;
}

export interface ImageMetadata {
  File?: FileMetadata;
  EXIF?: Record<string, unknown>;
  IPTC?: Record<string, unknown>;
  XMP?: Record<string, unknown>;
  [key: string]: unknown;
}

export interface FileMetadata {
  FileName: string;
  FileSize: number;
  FileModifyDate: string;
  ImageWidth: number;
  ImageHeight: number;
  Format: string;
  Mode: string;
}

export interface FolderStats {
  total_files: number;
  total_size: number;
  total_size_formatted: string;
  extensions: Record<string, number>;
  largest_file: string | null;
  smallest_file: string | null;
  average_size: number;
  average_size_formatted: string;
}

export interface MetadataSuggestion {
  value: string;
  count: number;
  lastUsed: string;
}

export interface NotificationData {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: number;
}

export interface AppSettings {
  autoSave: boolean;
  showSuggestions: boolean;
  backupBeforeEdit: boolean;
  theme: 'light' | 'dark' | 'auto';
}

// API response types
export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
}

export interface FolderScanResponse {
  images: ImageData[];
  total_count: number;
}

export interface MetadataUpdateResponse {
  success: boolean;
  message: string;
}

// Component prop types
export interface MetadataEditorProps {
  metadata: ImageMetadata;
  suggestions: Record<string, MetadataSuggestion[]>;
}

export interface ImagePreviewProps {
  image: ImageData;
}

export interface NotificationContainerProps {
  notifications: NotificationData[];
} 