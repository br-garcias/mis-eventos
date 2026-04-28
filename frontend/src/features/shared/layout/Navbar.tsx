import { useAuthRedirect } from '@/features/auth/hooks/useAuthRedirect';
import { useAuthStore } from '@/features/auth/store';
import { Avatar, AvatarFallback } from '@/features/shared/ui/Avatar';
import { cn } from '@/lib/cn';
import { getInitials } from '@/lib/initials';
import { ChevronDown, LogOut, Menu, Plus, Shield, User, X, Zap } from 'lucide-react';
import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';

export function Navbar() {
  const { user, logout, isOrganizer, isAdmin } = useAuthStore();
  const { redirectToAuth } = useAuthRedirect();
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);

  const isAuth = !!user;

  const navLinks = [
    { to: '/', label: 'Explorar' },
    ...(isAuth ? [{ to: '/perfil', label: 'Mis Eventos' }] : []),
  ];

  const handleLogout = () => {
    logout();
    setProfileOpen(false);
    navigate('/');
  };

  return (
    <header className="fixed top-0 left-0 right-0 z-40">
      <nav className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mt-3 glass rounded-2xl px-5 py-3 flex items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 rounded-xl bg-linear-to-br from-brand-400 to-brand-600 flex items-center justify-center shadow-lg shadow-brand-400/30 group-hover:shadow-brand-400/50 transition-all">
              <Zap size={16} className="text-white" fill="white" />
            </div>
            <span className="font-display font-bold text-white text-lg tracking-tight">
              Mis<span className="text-brand-400">Eventos</span>
            </span>
          </Link>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className={cn(
                  'px-4 py-2 rounded-xl text-sm font-body font-medium transition-all',
                  location.pathname === link.to
                    ? 'bg-white/10 text-white'
                    : 'text-white/60 hover:text-white hover:bg-white/5',
                )}
              >
                {link.label}
              </Link>
            ))}
          </div>

          {/* Right Actions */}
          <div className="hidden md:flex items-center gap-3">
            {isAuth && isOrganizer() && (
              <Link to="/eventos/crear">
                <button className="flex items-center gap-2 bg-brand-400 hover:bg-brand-300 text-white px-4 py-2 rounded-xl text-sm font-medium transition-all shadow-md shadow-brand-400/25 hover:shadow-brand-400/40">
                  <Plus size={16} />
                  Crear Evento
                </button>
              </Link>
            )}

            {isAuth ? (
              <div className="relative">
                <button
                  onClick={() => setProfileOpen(!profileOpen)}
                  className="flex items-center gap-2 glass px-3 py-2 rounded-xl hover:border-white/20 transition-all"
                >
                  <Avatar>
                    <AvatarFallback className="text-xs">{getInitials(user.name)}</AvatarFallback>
                  </Avatar>
                  <div className="text-left">
                    <p className="text-xs font-semibold text-white leading-none">
                      {user.name.split(' ')[0]}
                    </p>
                    <p className="text-xs text-white/40 mt-0.5">{user.role.name}</p>
                  </div>
                  <ChevronDown
                    size={14}
                    className={cn(
                      'text-white/40 transition-transform',
                      profileOpen && 'rotate-180',
                    )}
                  />
                </button>

                {profileOpen && (
                  <div className="absolute right-0 top-full mt-2 w-48 glass-sm rounded-xl py-1 shadow-xl border border-white/10">
                    <Link
                      to="/perfil"
                      className="flex items-center gap-2 px-4 py-2.5 text-sm text-white/70 hover:text-white hover:bg-white/5 transition-colors"
                      onClick={() => setProfileOpen(false)}
                    >
                      <User size={14} /> Mi Perfil
                    </Link>
                    {isAdmin() && (
                      <Link
                        to="/admin/users"
                        className="flex items-center gap-2 px-4 py-2.5 text-sm text-white/70 hover:text-white hover:bg-white/5 transition-colors"
                        onClick={() => setProfileOpen(false)}
                      >
                        <Shield size={14} /> Admin
                      </Link>
                    )}
                    <hr className="border-white/10 my-1" />
                    <button
                      onClick={handleLogout}
                      className="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-red-400 hover:bg-red-500/10 transition-colors"
                    >
                      <LogOut size={14} /> Cerrar Sesión
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <button
                  onClick={() => redirectToAuth('/login')}
                  className="px-4 py-2 text-sm font-medium text-white/70 hover:text-white transition-colors"
                >
                  Iniciar sesión
                </button>
                <button
                  onClick={() => redirectToAuth('/registro')}
                  className="bg-brand-400 hover:bg-brand-300 text-white px-4 py-2 rounded-xl text-sm font-medium transition-all shadow-md shadow-brand-400/25"
                >
                  Registrarse
                </button>
              </div>
            )}
          </div>

          {/* Mobile Menu Toggle */}
          <button
            className="md:hidden text-white/70 hover:text-white p-2 rounded-lg hover:bg-white/5 transition-colors"
            onClick={() => setMobileOpen(!mobileOpen)}
          >
            {mobileOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileOpen && (
          <div className="md:hidden mt-2 glass rounded-2xl p-4 flex flex-col gap-2 animate-fade-up">
            {navLinks.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className="px-4 py-3 rounded-xl text-sm font-medium text-white/70 hover:text-white hover:bg-white/5 transition-colors"
                onClick={() => setMobileOpen(false)}
              >
                {link.label}
              </Link>
            ))}
            {isAuth ? (
              <>
                {isOrganizer() && (
                  <Link
                    to="/eventos/crear"
                    className="flex items-center gap-2 bg-brand-400 text-white px-4 py-3 rounded-xl text-sm font-medium"
                    onClick={() => setMobileOpen(false)}
                  >
                    <Plus size={16} /> Crear Evento
                  </Link>
                )}
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-2 px-4 py-3 text-sm text-red-400 hover:bg-red-500/10 rounded-xl transition-colors"
                >
                  <LogOut size={16} /> Cerrar Sesión
                </button>
              </>
            ) : (
              <div className="flex gap-2 pt-2">
                <Link
                  to="/login"
                  className="flex-1 text-center py-2.5 rounded-xl border border-white/10 text-sm text-white/70"
                  onClick={() => setMobileOpen(false)}
                >
                  Iniciar sesión
                </Link>
                <Link
                  to="/registro"
                  className="flex-1 text-center py-2.5 rounded-xl bg-brand-400 text-white text-sm font-medium"
                  onClick={() => setMobileOpen(false)}
                >
                  Registrarse
                </Link>
              </div>
            )}
          </div>
        )}
      </nav>
    </header>
  );
}
