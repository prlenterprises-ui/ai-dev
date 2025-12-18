import { useState } from 'react'
import { Send, Users, Trophy, MessageSquare, Loader2 } from 'lucide-react'
import ReactMarkdown from 'react-markdown'

export default function CouncilPage() {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [activeTab, setActiveTab] = useState('final')
  const [selectedModel, setSelectedModel] = useState(0)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!query.trim() || loading) return

    setLoading(true)
    
    // Simulate council deliberation with mock data
    // In production, this would call the GraphQL mutation
    setTimeout(() => {
      setResult({
        query,
        individualResponses: [
          {
            model: 'openai/gpt-4o',
            content: `**GPT-4o's Analysis:**\n\nThis is a thoughtful question. Here's my perspective:\n\n1. **First point**: Consider the context carefully\n2. **Second point**: Evaluate multiple angles\n3. **Conclusion**: The answer depends on specific requirements\n\nI'd recommend...`,
            tokensUsed: 245,
            latencyMs: 1234,
          },
          {
            model: 'anthropic/claude-3-5-sonnet',
            content: `**Claude's Response:**\n\nLet me break this down systematically:\n\n- From a technical standpoint, there are several factors to consider\n- The key insight here is understanding the underlying principles\n- Based on best practices, I would suggest...\n\nIn summary, the most robust approach would be...`,
            tokensUsed: 312,
            latencyMs: 1156,
          },
          {
            model: 'google/gemini-2.0-flash',
            content: `**Gemini's Perspective:**\n\nGreat question! Here's how I see it:\n\n🔹 **Key Consideration 1**: Start with fundamentals\n🔹 **Key Consideration 2**: Build progressively\n🔹 **Key Consideration 3**: Test and iterate\n\nThe optimal solution would combine these elements effectively.`,
            tokensUsed: 198,
            latencyMs: 987,
          },
        ],
        rankings: ['claude-3-5-sonnet', 'gpt-4o', 'gemini-2.0-flash'],
        finalAnswer: `# Council Synthesis\n\nAfter reviewing all council members' responses, here is the synthesized answer:\n\n## Key Points\n\n1. **Consensus View**: All models agree that the approach should be systematic and well-structured.\n\n2. **Best Practices**: Claude provided the most comprehensive breakdown, while GPT-4o offered practical implementation advice.\n\n3. **Recommended Approach**: Combine the structured methodology from Claude with the actionable steps from GPT-4o.\n\n## Final Recommendation\n\nBased on the collective wisdom of the council, the optimal path forward involves:\n\n- Start with a clear understanding of requirements\n- Build incrementally with testing at each stage\n- Iterate based on feedback\n\nThis synthesized approach incorporates the strongest elements from each model's response.`,
        chairmanModel: 'gemini-pro-thinking',
      })
      setLoading(false)
    }, 2000)
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center gap-4">
        <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
          <Users className="text-white" size={28} />
        </div>
        <div>
          <h1 className="font-display text-3xl font-bold">LLM Council</h1>
          <p className="text-sand-400">Multi-model deliberation with peer review</p>
        </div>
      </div>

      {/* Query Input */}
      <form onSubmit={handleSubmit} className="card p-6">
        <label className="block text-sm font-medium text-sand-300 mb-3">
          Ask the Council
        </label>
        <div className="flex gap-4">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask a question to be deliberated by multiple LLMs..."
            className="flex-1 bg-[#252530] border border-[#3a3a45] rounded-xl px-4 py-3 text-white placeholder-sand-500 resize-none focus:outline-none focus:border-electric-500 transition-colors"
            rows={3}
          />
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="btn-primary self-end disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <Loader2 className="animate-spin" size={20} />
            ) : (
              <Send size={20} />
            )}
          </button>
        </div>
        
        {/* Model info */}
        <div className="mt-4 flex flex-wrap gap-2">
          {['GPT-4o', 'Claude 3.5 Sonnet', 'Gemini 2.0'].map((model) => (
            <span
              key={model}
              className="text-xs px-3 py-1 rounded-full bg-[#252530] text-sand-300"
            >
              {model}
            </span>
          ))}
          <span className="text-xs px-3 py-1 rounded-full bg-violet-500/20 text-violet-300">
            👑 Chairman: Gemini Pro Thinking
          </span>
        </div>
      </form>

      {/* Loading State */}
      {loading && (
        <div className="card p-12 text-center">
          <div className="inline-flex items-center gap-3 text-electric-400">
            <Loader2 className="animate-spin" size={24} />
            <span className="font-medium">Council is deliberating...</span>
          </div>
          <div className="mt-4 text-sm text-sand-500">
            Stage 1: Querying models → Stage 2: Peer review → Stage 3: Synthesis
          </div>
        </div>
      )}

      {/* Results */}
      {result && !loading && (
        <div className="space-y-6">
          {/* Tabs */}
          <div className="flex gap-2">
            {[
              { id: 'final', label: 'Final Answer', icon: Trophy },
              { id: 'individual', label: 'Individual Responses', icon: MessageSquare },
              { id: 'rankings', label: 'Rankings', icon: Trophy },
            ].map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors
                    ${activeTab === tab.id
                      ? 'bg-electric-500/20 text-electric-400'
                      : 'text-sand-400 hover:text-white hover:bg-white/5'
                    }
                  `}
                >
                  <Icon size={16} />
                  {tab.label}
                </button>
              )
            })}
          </div>

          {/* Final Answer */}
          {activeTab === 'final' && (
            <div className="card p-6 border-electric-500/30 bg-gradient-to-br from-electric-500/5 to-transparent">
              <div className="flex items-center gap-2 mb-4 text-electric-400">
                <Trophy size={20} />
                <span className="font-semibold">Chairman's Synthesis</span>
                <span className="text-xs text-sand-500">({result.chairmanModel})</span>
              </div>
              <div className="markdown-content">
                <ReactMarkdown>{result.finalAnswer}</ReactMarkdown>
              </div>
            </div>
          )}

          {/* Individual Responses */}
          {activeTab === 'individual' && (
            <div className="card overflow-hidden">
              {/* Model Tabs */}
              <div className="flex border-b border-[#2a2a35]">
                {result.individualResponses.map((resp, idx) => (
                  <button
                    key={resp.model}
                    onClick={() => setSelectedModel(idx)}
                    className={`
                      flex-1 px-4 py-3 text-sm font-medium transition-colors
                      ${selectedModel === idx
                        ? 'bg-[#252530] text-white border-b-2 border-electric-500'
                        : 'text-sand-400 hover:text-white hover:bg-white/5'
                      }
                    `}
                  >
                    {resp.model.split('/')[1]}
                  </button>
                ))}
              </div>
              
              {/* Response Content */}
              <div className="p-6">
                <div className="flex justify-between items-center mb-4 text-xs text-sand-500">
                  <span>{result.individualResponses[selectedModel].model}</span>
                  <span>
                    {result.individualResponses[selectedModel].tokensUsed} tokens • 
                    {result.individualResponses[selectedModel].latencyMs}ms
                  </span>
                </div>
                <div className="markdown-content">
                  <ReactMarkdown>
                    {result.individualResponses[selectedModel].content}
                  </ReactMarkdown>
                </div>
              </div>
            </div>
          )}

          {/* Rankings */}
          {activeTab === 'rankings' && (
            <div className="card p-6">
              <h3 className="font-semibold mb-4">Aggregate Rankings (by peer review)</h3>
              <div className="space-y-3">
                {result.rankings.map((model, idx) => (
                  <div
                    key={model}
                    className="flex items-center gap-4 p-4 rounded-lg bg-[#252530]"
                  >
                    <div className={`
                      w-10 h-10 rounded-full flex items-center justify-center font-bold
                      ${idx === 0 ? 'bg-yellow-500/20 text-yellow-400' : 
                        idx === 1 ? 'bg-gray-400/20 text-gray-300' :
                        'bg-amber-700/20 text-amber-600'}
                    `}>
                      #{idx + 1}
                    </div>
                    <div className="flex-1">
                      <div className="font-medium">{model}</div>
                      <div className="text-sm text-sand-500">
                        Average position: {(idx + 1 + Math.random() * 0.5).toFixed(2)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <p className="mt-4 text-xs text-sand-500">
                Note: Rankings are based on anonymous peer review. Each model evaluates 
                others' responses without knowing which model produced them.
              </p>
            </div>
          )}
        </div>
      )}

      {/* How it works */}
      {!result && !loading && (
        <div className="card p-8">
          <h2 className="font-display text-xl font-bold mb-6">How LLM Council Works</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="p-4 rounded-xl bg-[#252530]/50">
              <div className="text-2xl mb-3">1️⃣</div>
              <h3 className="font-semibold mb-2">Stage 1: First Opinions</h3>
              <p className="text-sm text-sand-400">
                Your query is sent to all council models in parallel. Each responds independently.
              </p>
            </div>
            <div className="p-4 rounded-xl bg-[#252530]/50">
              <div className="text-2xl mb-3">2️⃣</div>
              <h3 className="font-semibold mb-2">Stage 2: Peer Review</h3>
              <p className="text-sm text-sand-400">
                Each model reviews all responses (anonymized) and ranks them by quality.
              </p>
            </div>
            <div className="p-4 rounded-xl bg-[#252530]/50">
              <div className="text-2xl mb-3">3️⃣</div>
              <h3 className="font-semibold mb-2">Stage 3: Synthesis</h3>
              <p className="text-sm text-sand-400">
                The Chairman model synthesizes the best answer using all responses and rankings.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

