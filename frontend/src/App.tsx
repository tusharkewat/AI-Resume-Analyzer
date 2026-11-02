import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import { Navbar } from './components/Navbar';
import { ProtectedRoute } from './components/ProtectedRoute';

// Pages
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { DashboardPage } from './pages/DashboardPage';
import { AnalyzePage } from './pages/AnalyzePage';
import { AnalysisResultPage } from './pages/AnalysisResultPage';
import { HistoryPage } from './pages/HistoryPage';
import { SettingsPage } from './pages/SettingsPage';

const AppContent: React.FC = () => {
  const { isAuthenticated, loading } = useAuth();
  const [currentPath, setCurrentPath] = useState(window.location.pathname || '/');

  useEffect(() => {
    const handlePopState = () => {
      setCurrentPath(window.location.pathname);
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    setCurrentPath(path);
    window.scrollTo(0, 0);
  };

  // Route matching helper
  const renderRoute = () => {
    if (loading) {
      return (
        <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center">
          <div className="w-10 h-10 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
        </div>
      );
    }

    // Dynamic route: /analysis/:id
    const analysisMatch = currentPath.match(/^\/analysis\/(\d+)$/);
    if (analysisMatch) {
      const id = parseInt(analysisMatch[1], 10);
      return (
        <ProtectedRoute>
          <AnalysisResultPage analysisId={id} navigate={navigate} />
        </ProtectedRoute>
      );
    }

    switch (currentPath) {
      case '/':
        return isAuthenticated ? (
          <ProtectedRoute>
            <DashboardPage navigate={navigate} />
          </ProtectedRoute>
        ) : (
          <LandingPage navigate={navigate} />
        );

      case '/login':
        return isAuthenticated ? (
          <DashboardPage navigate={navigate} />
        ) : (
          <LoginPage navigate={navigate} />
        );

      case '/register':
        return isAuthenticated ? (
          <DashboardPage navigate={navigate} />
        ) : (
          <RegisterPage navigate={navigate} />
        );

      case '/dashboard':
        return (
          <ProtectedRoute>
            <DashboardPage navigate={navigate} />
          </ProtectedRoute>
        );

      case '/analyze':
        return (
          <ProtectedRoute>
            <AnalyzePage navigate={navigate} />
          </ProtectedRoute>
        );

      case '/history':
        return (
          <ProtectedRoute>
            <HistoryPage navigate={navigate} />
          </ProtectedRoute>
        );

      case '/settings':
        return (
          <ProtectedRoute>
            <SettingsPage navigate={navigate} />
          </ProtectedRoute>
        );

      default:
        return (
          <div className="max-w-md mx-auto px-4 py-20 text-center space-y-4">
            <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Page Not Found</h2>
            <p className="text-sm text-slate-500">The requested page does not exist.</p>
            <button
              onClick={() => navigate('/')}
              className="px-4 py-2 text-sm font-semibold text-white bg-indigo-600 rounded-lg"
            >
              Back to Home
            </button>
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100 transition-colors">
      <Navbar currentPath={currentPath} navigate={navigate} />
      <main className="flex-1">
        {renderRoute()}
      </main>
    </div>
  );
};

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </ThemeProvider>
  );
}
