import { Link } from 'react-router-dom'
import { ArrowRight, Zap, Brain, Target, FileText, Users, Bird, Sparkles } from 'lucide-react'

const modules = [
  {
    id: 'council',
    name: 'LLM Council',
    description: 'Query multiple LLMs, have them peer-review each other, get a synthesized answer from a Chairman model.',
    icon: Users,
    color: 'from-violet-500 to-purple-600',
    route: '/council',
    status: 'active',
    features: ['Multi-model deliberation', 'Anonymous peer review', 'Aggregate rankings'],
  },
  {
    id: 'jobbernaut',
    name: 'Jobbernaut Tailor',
    description: 'Industrial-scale resume tailoring with AI validation. Process 100+ applications per day.',
    icon: FileText,
    color: 'from-electric-500 to-cyan-600',
    route: '/jobbernaut',
    status: 'active',
    features: ['12-step pipeline', 'Self-healing validation', 'ATS optimization'],
  },
  {
    id: 'matcher',
    name: 'Resume Matcher',
    description: 'Local AI resume analysis using Ollama. Privacy-preserving ATS scoring and keyword optimization.',
    icon: Target,
    color: 'from-emerald-500 to-teal-600',
    route: '/matcher',
    status: 'active',
    features: ['Local inference', 'ATS compatibility', 'Keyword analysis'],
  },
  {
    id: 'resume-lm',
    name: 'ResumeLM',
    description: 'Full-featured AI resume builder with dashboard, AI assistant, and real-time scoring.',
    icon: Sparkles,
    color: 'from-amber-500 to-orange-600',
    route: '/resume-lm',
    status: 'coming_soon',
    features: ['AI assistant', 'PDF generation', 'Cover letters'],
  },
  {
    id: 'aihawk',
    name: 'AIHawk',
    description: 'Automated job application agent. Web automation for bulk applications on job platforms.',
    icon: Bird,
    color: 'from-rose-500 to-pink-600',
    route: '/aihawk',
    status: 'coming_soon',
    features: ['Web automation', 'Bulk applications', 'Smart filtering'],
  },
]

export default function HomePage() {
  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <section className="text-center pt-12 pb-8">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-electric-500/10 border border-electric-500/30 text-electric-400 text-sm mb-8">
          <Zap size={16} />
          <span>Learning AI Integration Through Building</span>
        </div>
        
        <h1 className="font-display text-5xl md:text-6xl font-bold mb-6">
          <span className="text-gradient">AI Dev Portal</span>
        </h1>
        
        <p className="text-xl text-sand-400 max-w-2xl mx-auto mb-8">
          A unified portal combining 5 AI-powered resume and job search tools.
          Learn how to integrate LLMs into web applications through hands-on exploration.
        </p>

        <div className="flex items-center justify-center gap-4">
          <Link to="/council" className="btn-primary flex items-center gap-2">
            <Brain size={20} />
            Try LLM Council
          </Link>
          <a 
            href="http://localhost:8000/graphql" 
            target="_blank" 
            rel="noopener noreferrer"
            className="btn-secondary"
          >
            GraphQL Playground
          </a>
        </div>
      </section>

      {/* Architecture Overview */}
      <section className="card p-8">
        <h2 className="font-display text-2xl font-bold mb-6 flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-electric-500/20 flex items-center justify-center">
            <Zap className="text-electric-400" size={20} />
          </div>
          Architecture
        </h2>
        
        <div className="grid md:grid-cols-3 gap-6 text-center">
          <div className="p-6 rounded-xl bg-[#252530]/50">
            <div className="text-3xl mb-3">⚛️</div>
            <h3 className="font-semibold mb-2">Frontend</h3>
            <p className="text-sm text-sand-400">React + Vite + Apollo Client</p>
            <p className="text-xs text-sand-500 mt-2">Port 5173</p>
          </div>
          <div className="p-6 rounded-xl bg-[#252530]/50">
            <div className="text-3xl mb-3">📡</div>
            <h3 className="font-semibold mb-2">GraphQL API</h3>
            <p className="text-sm text-sand-400">FastAPI + Strawberry</p>
            <p className="text-xs text-sand-500 mt-2">Port 8000/graphql</p>
          </div>
          <div className="p-6 rounded-xl bg-[#252530]/50">
            <div className="text-3xl mb-3">🧠</div>
            <h3 className="font-semibold mb-2">AI Layer</h3>
            <p className="text-sm text-sand-400">OpenRouter + Ollama</p>
            <p className="text-xs text-sand-500 mt-2">Multi-provider</p>
          </div>
        </div>
      </section>

      {/* Modules Grid */}
      <section>
        <h2 className="font-display text-3xl font-bold mb-8 text-center">
          Integrated Modules
        </h2>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {modules.map((module) => {
            const Icon = module.icon
            const isComingSoon = module.status === 'coming_soon'
            
            return (
              <Link
                key={module.id}
                to={module.route}
                className={`
                  card card-hover p-6 flex flex-col
                  ${isComingSoon ? 'opacity-60' : ''}
                `}
              >
                {/* Icon */}
                <div className={`
                  w-14 h-14 rounded-xl bg-gradient-to-br ${module.color}
                  flex items-center justify-center mb-4
                `}>
                  <Icon className="text-white" size={28} />
                </div>

                {/* Title & Status */}
                <div className="flex items-center gap-2 mb-2">
                  <h3 className="font-display text-xl font-semibold">{module.name}</h3>
                  {isComingSoon && (
                    <span className="text-xs bg-[#2a2a35] px-2 py-1 rounded-full text-sand-400">
                      Soon
                    </span>
                  )}
                </div>

                {/* Description */}
                <p className="text-sand-400 text-sm mb-4 flex-grow">
                  {module.description}
                </p>

                {/* Features */}
                <div className="flex flex-wrap gap-2 mb-4">
                  {module.features.map((feature) => (
                    <span
                      key={feature}
                      className="text-xs px-2 py-1 rounded-md bg-[#252530] text-sand-300"
                    >
                      {feature}
                    </span>
                  ))}
                </div>

                {/* CTA */}
                <div className="flex items-center gap-2 text-electric-400 text-sm font-medium">
                  <span>{isComingSoon ? 'Coming soon' : 'Explore'}</span>
                  <ArrowRight size={16} />
                </div>
              </Link>
            )
          })}
        </div>
      </section>

      {/* Quick Start */}
      <section className="card p-8">
        <h2 className="font-display text-2xl font-bold mb-6">Quick Start</h2>
        
        <div className="space-y-4 font-mono text-sm">
          <div className="p-4 rounded-lg bg-[#252530]">
            <p className="text-sand-400 mb-2"># Start the backend</p>
            <p className="text-electric-400">cd apps/portal-python && uv run python main.py</p>
          </div>
          <div className="p-4 rounded-lg bg-[#252530]">
            <p className="text-sand-400 mb-2"># Start the frontend</p>
            <p className="text-electric-400">cd apps/portal-ui && npm install && npm run dev</p>
          </div>
          <div className="p-4 rounded-lg bg-[#252530]">
            <p className="text-sand-400 mb-2"># Open in browser</p>
            <p className="text-electric-400">http://localhost:5173</p>
          </div>
        </div>
      </section>
    </div>
  )
}

