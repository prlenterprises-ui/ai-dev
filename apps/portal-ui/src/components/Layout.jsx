import { Outlet, Link, useLocation } from 'react-router-dom'
import { Home, Users, FileText, Target, Sparkles, Bird, Zap } from 'lucide-react'

const navItems = [
  { path: '/', label: 'Home', icon: Home },
  { path: '/council', label: 'LLM Council', icon: Users },
  { path: '/jobbernaut', label: 'Jobbernaut', icon: FileText },
  { path: '/matcher', label: 'Resume Matcher', icon: Target },
  { path: '/auto-apply', label: 'Auto Apply', icon: Zap },
  { path: '/resume-lm', label: 'ResumeLM', icon: Sparkles, disabled: true },
  { path: '/aihawk', label: 'AIHawk', icon: Bird, disabled: true },
]

export default function Layout() {
  const location = useLocation()

  return (
    <div className="min-h-screen gradient-bg">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-[#0f0f12]/80 backdrop-blur-xl border-b border-[#2a2a35]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-electric-500 to-coral-500 flex items-center justify-center">
                <span className="text-xl">🧠</span>
              </div>
              <span className="font-display font-bold text-xl">AI Dev Portal</span>
            </Link>

            {/* Nav Links */}
            <div className="hidden md:flex items-center gap-1">
              {navItems.map((item) => {
                const Icon = item.icon
                const isActive = location.pathname === item.path
                
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`
                      flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium
                      transition-all duration-200
                      ${isActive 
                        ? 'bg-electric-500/20 text-electric-400' 
                        : 'text-sand-400 hover:text-white hover:bg-white/5'
                      }
                      ${item.disabled ? 'opacity-50 cursor-not-allowed' : ''}
                    `}
                  >
                    <Icon size={18} />
                    <span>{item.label}</span>
                    {item.disabled && (
                      <span className="text-xs bg-[#2a2a35] px-2 py-0.5 rounded-full">Soon</span>
                    )}
                  </Link>
                )
              })}
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="pt-20 pb-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="border-t border-[#2a2a35] py-8">
        <div className="max-w-7xl mx-auto px-4 text-center text-sand-500 text-sm">
          <p>AI Dev Portal — Learning AI integration through unified tooling</p>
          <p className="mt-2 text-sand-600">
            Combining: Jobbernaut • LLM Council • Resume Matcher • ResumeLM • AIHawk
          </p>
        </div>
      </footer>
    </div>
  )
}

