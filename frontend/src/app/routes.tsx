import { RedirectIfAuth, RequireAuth } from '@/features/auth/ui/RequireAuth';
import { LoginSkeleton } from '@/features/auth/ui/skeletons/LoginSkeleton';
import { RegisterSkeleton } from '@/features/auth/ui/skeletons/RegisterSkeleton';
import { ProfileSkeleton } from '@/features/profile/ui/skeletons/ProfileSkeleton';
import { ForbiddenPage } from '@/features/shared/ui/ForbiddenPage';
import { NotFound } from '@/features/shared/ui/NotFound';
import { Spinner } from '@/features/shared/ui/Spinner';
import { AdminUsersSkeleton } from '@/features/users/ui/skeletons/AdminUsersSkeleton';
import { lazy, Suspense } from 'react';
import { Route, Routes } from 'react-router-dom';

function PageLoader() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <Spinner size="lg" />
    </div>
  );
}

const HomePage = lazy(() =>
  import('@/features/events/ui/HomePage').then((m) => ({ default: m.HomePage })),
);
const EventDetailPage = lazy(() =>
  import('@/features/events/ui/EventDetailPage').then((m) => ({ default: m.EventDetailPage })),
);
const CreateEventPage = lazy(() =>
  import('@/features/events/ui/CreateEventPage').then((m) => ({ default: m.CreateEventPage })),
);
const EditEventPage = lazy(() =>
  import('@/features/events/ui/EditEventPage').then((m) => ({ default: m.EditEventPage })),
);
const ProfilePage = lazy(() =>
  import('@/features/profile/ui/ProfilePage').then((m) => ({ default: m.ProfilePage })),
);
const LoginPage = lazy(() =>
  import('@/features/auth/ui/LoginPage').then((m) => ({ default: m.LoginPage })),
);
const RegisterPage = lazy(() =>
  import('@/features/auth/ui/RegisterPage').then((m) => ({ default: m.RegisterPage })),
);
const AdminUsersPage = lazy(() =>
  import('@/features/users/ui/AdminUsersPage').then((m) => ({ default: m.AdminUsersPage })),
);

export function AppRoutes() {
  return (
    <Routes>
      <Route
        path="/"
        element={
          <Suspense fallback={<PageLoader />}>
            <HomePage />
          </Suspense>
        }
      />
      <Route
        path="/eventos/:id"
        element={
          <Suspense fallback={<PageLoader />}>
            <EventDetailPage />
          </Suspense>
        }
      />
      <Route
        path="/eventos/crear"
        element={
          <RequireAuth>
            <Suspense fallback={<PageLoader />}>
              <CreateEventPage />
            </Suspense>
          </RequireAuth>
        }
      />
      <Route
        path="/eventos/:id/editar"
        element={
          <RequireAuth roles={['admin', 'organizer']}>
            <Suspense fallback={<PageLoader />}>
              <EditEventPage />
            </Suspense>
          </RequireAuth>
        }
      />
      <Route
        path="/perfil"
        element={
          <RequireAuth>
            <Suspense fallback={<ProfileSkeleton />}>
              <ProfilePage />
            </Suspense>
          </RequireAuth>
        }
      />
      <Route
        path="/login"
        element={
          <RedirectIfAuth>
            <Suspense fallback={<LoginSkeleton />}>
              <LoginPage />
            </Suspense>
          </RedirectIfAuth>
        }
      />
      <Route
        path="/registro"
        element={
          <RedirectIfAuth>
            <Suspense fallback={<RegisterSkeleton />}>
              <RegisterPage />
            </Suspense>
          </RedirectIfAuth>
        }
      />
      <Route
        path="/admin/users"
        element={
          <RequireAuth roles={['admin']}>
            <Suspense fallback={<AdminUsersSkeleton />}>
              <AdminUsersPage />
            </Suspense>
          </RequireAuth>
        }
      />
      <Route path="/403" element={<ForbiddenPage />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
