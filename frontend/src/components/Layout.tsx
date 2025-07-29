import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  HomeIcon, 
  PhotoIcon, 
  Cog6ToothIcon,
  Bars3Icon,
  XMarkIcon,
  FolderIcon
} from '@heroicons/react/24/outline';
import { useFolder } from '../contexts/FolderContext';
import { useNotification } from '../contexts/NotificationContext';
import NotificationContainer from './NotificationContainer';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const { state: folderState } = useFolder();
  const { state: notificationState } = useNotification();

  const navigation = [
    { name: 'Home', href: '/', icon: HomeIcon },
    { name: 'Editor', href: '/editor', icon: PhotoIcon },
    { name: 'Settings', href: '/settings', icon: Cog6ToothIcon },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="min-h-screen bg-secondary-50 dark:bg-secondary-900">
      {/* Sidebar */}
      <div className={`sidebar ${sidebarOpen ? 'sidebar-open' : 'sidebar-closed'} lg:translate-x-0`}>
        <div className="flex h-full flex-col">
          {/* Logo */}
          <div className="flex h-16 items-center justify-between px-6 border-b border-secondary-200 dark:border-secondary-700">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
                <PhotoIcon className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-semibold font-display">Metadata Editor</h1>
              </div>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden p-1 rounded-lg text-secondary-400 hover:text-secondary-600 hover:bg-secondary-100 dark:text-secondary-500 dark:hover:text-secondary-300 dark:hover:bg-secondary-700"
            >
              <XMarkIcon className="w-5 h-5" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2">
            {navigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={`flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors duration-200 ${
                  isActive(item.href)
                    ? 'bg-primary-100 text-primary-700 border border-primary-200 dark:bg-primary-900 dark:text-primary-300 dark:border-primary-700'
                    : 'text-secondary-600 hover:text-secondary-900 hover:bg-secondary-100 dark:text-secondary-400 dark:hover:text-secondary-200 dark:hover:bg-secondary-700'
                }`}
                onClick={() => setSidebarOpen(false)}
              >
                <item.icon className="w-5 h-5 mr-3" />
                {item.name}
              </Link>
            ))}
          </nav>

          {/* Current Folder */}
          {folderState.selectedFolder && (
            <div className="px-4 py-4 border-t border-secondary-200 dark:border-secondary-700">
              <div className="flex items-center space-x-2 text-sm text-secondary">
                <FolderIcon className="w-4 h-4" />
                <span className="truncate">
                  {folderState.selectedFolder.split('/').pop() || folderState.selectedFolder}
                </span>
              </div>
              {folderState.images.length > 0 && (
                <p className="text-xs text-muted mt-1">
                  {folderState.images.length} images
                </p>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Mobile menu button - positioned absolutely for mobile */}
        <button
          onClick={() => setSidebarOpen(true)}
          className="lg:hidden fixed top-4 left-4 z-50 p-2 rounded-lg bg-white dark:bg-secondary-800 shadow-lg text-secondary-400 hover:text-secondary-600 hover:bg-secondary-100 dark:text-secondary-500 dark:hover:text-secondary-300 dark:hover:bg-secondary-700 border border-secondary-200 dark:border-secondary-600"
        >
          <Bars3Icon className="w-5 h-5" />
        </button>

        {/* Page content with top padding to compensate for removed navbar */}
        <main className="main-content">
          <div className="px-4 pt-24 pb-6 sm:px-6 lg:px-8 lg:pt-20">
            {children}
          </div>
        </main>
      </div>

      {/* Notifications */}
      <NotificationContainer notifications={notificationState.notifications} />

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-secondary-900 bg-opacity-50 dark:bg-opacity-70 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
};

export default Layout; 