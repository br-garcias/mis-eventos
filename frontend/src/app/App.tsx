import { AuthProvider } from '@/features/auth/ui/AuthProvider';
import { Navbar } from '@/features/shared/layout/Navbar';
import { DialogManager } from '@/features/shared/ui/DialogManager';
import { PageLoader } from '@/features/shared/ui/PageLoader';
import { Suspense } from 'react';
import { BrowserRouter } from 'react-router-dom';
import { Toaster } from 'sonner';
import { AppRoutes } from './routes';

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <div className="min-h-screen bg-surface noise-bg">
          <Navbar />
          <Suspense fallback={<PageLoader />}>
            <AppRoutes />
          </Suspense>
          <Toaster position="top-center" richColors />
          <DialogManager />
        </div>
      </AuthProvider>
    </BrowserRouter>
  );
}
