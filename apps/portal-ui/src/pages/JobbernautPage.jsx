import { useState } from 'react'
import { FileText, Play, CheckCircle, Circle, Loader2, Download } from 'lucide-react'

const PIPELINE_STEPS = [
  { id: '1', name: 'Job Resonance Analysis', stage: 'intelligence', status: 'pending' },
  { id: '2', name: 'Company Research', stage: 'intelligence', status: 'pending' },
  { id: '3', name: 'Storytelling Arc', stage: 'intelligence', status: 'pending' },
  { id: '4', name: 'Resume JSON Generation', stage: 'generation', status: 'pending' },
  { id: '5', name: 'Cover Letter Generation', stage: 'generation', status: 'pending' },
  { id: '6', name: 'LaTeX Rendering', stage: 'rendering', status: 'pending' },
  { id: '7', name: 'PDF Compilation', stage: 'rendering', status: 'pending' },
]

export default function JobbernautPage() {
  const [jobTitle, setJobTitle] = useState('')
  const [company, setCompany] = useState('')
  const [jobDescription, setJobDescription] = useState('')
  const [processing, setProcessing] = useState(false)
  const [steps, setSteps] = useState(PIPELINE_STEPS)
  const [completed, setCompleted] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!jobTitle || !company || !jobDescription) return

    setProcessing(true)
    setCompleted(false)
    setSteps(PIPELINE_STEPS.map(s => ({ ...s, status: 'pending' })))

    // Simulate pipeline execution
    for (let i = 0; i < PIPELINE_STEPS.length; i++) {
      setSteps(prev => prev.map((s, idx) => ({
        ...s,
        status: idx === i ? 'running' : idx < i ? 'completed' : 'pending'
      })))
      
      // Simulate processing time
      await new Promise(resolve => setTimeout(resolve, 1500 + Math.random() * 1000))
    }

    setSteps(prev => prev.map(s => ({ ...s, status: 'completed' })))
    setProcessing(false)
    setCompleted(true)
  }

  const getStageColor = (stage) => {
    switch (stage) {
      case 'intelligence': return 'text-violet-400'
      case 'generation': return 'text-electric-400'
      case 'rendering': return 'text-emerald-400'
      default: return 'text-sand-400'
    }
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center gap-4">
        <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-electric-500 to-cyan-600 flex items-center justify-center">
          <FileText className="text-white" size={28} />
        </div>
        <div>
          <h1 className="font-display text-3xl font-bold">Jobbernaut Tailor</h1>
          <p className="text-sand-400">Industrial-scale resume tailoring with AI validation</p>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Input Form */}
        <div className="card p-6">
          <h2 className="font-semibold text-lg mb-4">Job Details</h2>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm text-sand-400 mb-2">Job Title</label>
              <input
                type="text"
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
                placeholder="Senior Software Engineer"
                className="w-full bg-[#252530] border border-[#3a3a45] rounded-lg px-4 py-3 text-white placeholder-sand-500 focus:outline-none focus:border-electric-500 transition-colors"
              />
            </div>
            
            <div>
              <label className="block text-sm text-sand-400 mb-2">Company</label>
              <input
                type="text"
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                placeholder="TechCorp Inc."
                className="w-full bg-[#252530] border border-[#3a3a45] rounded-lg px-4 py-3 text-white placeholder-sand-500 focus:outline-none focus:border-electric-500 transition-colors"
              />
            </div>
            
            <div>
              <label className="block text-sm text-sand-400 mb-2">Job Description</label>
              <textarea
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Paste the full job description here..."
                rows={8}
                className="w-full bg-[#252530] border border-[#3a3a45] rounded-lg px-4 py-3 text-white placeholder-sand-500 resize-none focus:outline-none focus:border-electric-500 transition-colors"
              />
            </div>

            <button
              type="submit"
              disabled={processing || !jobTitle || !company || !jobDescription}
              className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {processing ? (
                <>
                  <Loader2 className="animate-spin" size={20} />
                  Processing...
                </>
              ) : (
                <>
                  <Play size={20} />
                  Start Pipeline
                </>
              )}
            </button>
          </form>
        </div>

        {/* Pipeline Progress */}
        <div className="card p-6">
          <h2 className="font-semibold text-lg mb-4">12-Step Pipeline</h2>
          
          <div className="space-y-3">
            {steps.map((step, idx) => (
              <div
                key={step.id}
                className={`
                  flex items-center gap-3 p-3 rounded-lg transition-colors
                  ${step.status === 'running' ? 'bg-electric-500/10 border border-electric-500/30' : 
                    step.status === 'completed' ? 'bg-emerald-500/10' : 'bg-[#252530]/50'}
                `}
              >
                {/* Status Icon */}
                <div className="flex-shrink-0">
                  {step.status === 'completed' ? (
                    <CheckCircle className="text-emerald-400" size={20} />
                  ) : step.status === 'running' ? (
                    <Loader2 className="text-electric-400 animate-spin" size={20} />
                  ) : (
                    <Circle className="text-sand-600" size={20} />
                  )}
                </div>
                
                {/* Step Info */}
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className={`text-xs uppercase ${getStageColor(step.stage)}`}>
                      {step.stage}
                    </span>
                  </div>
                  <span className={step.status === 'pending' ? 'text-sand-500' : 'text-white'}>
                    {step.name}
                  </span>
                </div>

                {/* Step Number */}
                <span className="text-xs text-sand-600">
                  {idx + 1}/7
                </span>
              </div>
            ))}
          </div>

          {/* Completion */}
          {completed && (
            <div className="mt-6 p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/30">
              <div className="flex items-center gap-2 text-emerald-400 mb-3">
                <CheckCircle size={20} />
                <span className="font-semibold">Pipeline Complete!</span>
              </div>
              <div className="space-y-2">
                <button className="w-full btn-secondary flex items-center justify-center gap-2">
                  <Download size={18} />
                  Download Resume PDF
                </button>
                <button className="w-full btn-secondary flex items-center justify-center gap-2">
                  <Download size={18} />
                  Download Cover Letter PDF
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Features */}
      <div className="grid md:grid-cols-3 gap-6">
        <div className="card p-6">
          <div className="text-3xl mb-4">⚡</div>
          <h3 className="font-semibold mb-2">Parallel Processing</h3>
          <p className="text-sm text-sand-400">
            Process up to 10 applications simultaneously with semaphore-based concurrency control.
          </p>
        </div>
        <div className="card p-6">
          <div className="text-3xl mb-4">🔄</div>
          <h3 className="font-semibold mb-2">Self-Healing Validation</h3>
          <p className="text-sm text-sand-400">
            Automatic retry with error feedback. 96%+ success rate after self-healing.
          </p>
        </div>
        <div className="card p-6">
          <div className="text-3xl mb-4">📄</div>
          <h3 className="font-semibold mb-2">ATS Optimized</h3>
          <p className="text-sm text-sand-400">
            Character limits, format standardization, and LaTeX-safe content for ATS compatibility.
          </p>
        </div>
      </div>
    </div>
  )
}

