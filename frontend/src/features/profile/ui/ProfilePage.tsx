import { useAuthStore } from '@/features/auth/store';
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { OrganizedEventsSection } from './OrganizedEventsSection';
import { RegisteredEventsSection } from './RegisteredEventsSection';

export function ProfilePage() {
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);
  const isOrganizer = useAuthStore((s) => s.isOrganizer);

  useEffect(() => {
    if (!user) navigate('/login');
  }, [user, navigate]);

  if (!user) return null;

  return (
    <div className="min-h-screen pt-28 pb-20">
      <div className="max-w-4xl mx-auto px-4 sm:px-6">
        <RegisteredEventsSection />
        {isOrganizer() && <OrganizedEventsSection />}
      </div>
    </div>
  );
}
