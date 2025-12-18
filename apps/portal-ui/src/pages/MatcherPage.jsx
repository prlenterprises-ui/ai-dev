import { useState } from 'react'
import { Target, Upload, Loader2, CheckCircle, AlertCircle, Lightbulb } from 'lucide-react'

export default function MatcherPage() {
    const [resumeText, setResumeText] = useState('')
    const [jobDescription, setJobDescription] = useState('')
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState(null)

    const handleAnalyze = async () => {
        if (!resumeText || !jobDescription) return

        setLoading(true)

        // Simulate analysis with mock data
        // In production, this would call the GraphQL mutation
        setTimeout(() => {
            setResult({
                overallScore: 72,
                keywordMatch: 68,
                atsCompatibility: 85,
                suggestions: [
                    'Add quantifiable achievements (e.g., "increased performance by 40%")',
                    'Include keywords: "distributed systems", "microservices", "Kubernetes"',
                    'Shorten bullet points to under 118 characters for better ATS parsing',
                    'Add a skills section with technical competencies',
                    'Use action verbs at the start of each bullet point',
                ],
                matchedKeywords: [
                    'Python', 'JavaScript', 'React', 'AWS', 'PostgreSQL',
                    'CI/CD', 'Agile', 'REST API', 'Git'
                ],
                missingKeywords: [
                    'Kubernetes', 'Docker', 'Microservices', 'GraphQL',
                    'TypeScript', 'Redis', 'Terraform'
                ],
            })
            setLoading(false)
        }, 2500)
    }

    const getScoreColor = (score) => {
        if (score >= 80) return 'text-emerald-400'
        if (score >= 60) return 'text-amber-400'
        return 'text-red-400'
    }

    const getScoreBg = (score) => {
        if (score >= 80) return 'bg-emerald-500'
        if (score >= 60) return 'bg-amber-500'
        return 'bg-red-500'
    }

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex items-center gap-4">
                <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center">
                    <Target className="text-white" size={28} />
                </div>
                <div>
                    <h1 className="font-display text-3xl font-bold">Resume Matcher</h1>
                    <p className="text-sand-400">Local AI resume analysis with Ollama</p>
                </div>
            </div>

            {/* Privacy Notice */}
            <div className="card p-4 border-emerald-500/30 bg-emerald-500/5">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center">
                        <CheckCircle className="text-emerald-400" size={20} />
                    </div>
                    <div>
                        <h3 className="font-medium text-emerald-400">Privacy-First Analysis</h3>
                        <p className="text-sm text-sand-400">
                            Your resume and job descriptions are processed locally using Ollama. No data leaves your machine.
                        </p>
                    </div>
                </div>
            </div>

            {/* Input Section */}
            <div className="grid lg:grid-cols-2 gap-6">
                {/* Resume Input */}
                <div className="card p-6">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="font-semibold">Your Resume</h2>
                        <button className="text-xs text-electric-400 hover:text-electric-300 flex items-center gap-1">
                            <Upload size={14} />
                            Upload PDF
                        </button>
                    </div>
                    <textarea
                        value={resumeText}
                        onChange={(e) => setResumeText(e.target.value)}
                        placeholder="Paste your resume text here..."
                        rows={12}
                        className="w-full bg-[#252530] border border-[#3a3a45] rounded-lg px-4 py-3 text-white placeholder-sand-500 resize-none focus:outline-none focus:border-electric-500 transition-colors font-mono text-sm"
                    />
                </div>

                {/* Job Description Input */}
                <div className="card p-6">
                    <h2 className="font-semibold mb-4">Job Description</h2>
                    <textarea
                        value={jobDescription}
                        onChange={(e) => setJobDescription(e.target.value)}
                        placeholder="Paste the job description here..."
                        rows={12}
                        className="w-full bg-[#252530] border border-[#3a3a45] rounded-lg px-4 py-3 text-white placeholder-sand-500 resize-none focus:outline-none focus:border-electric-500 transition-colors font-mono text-sm"
                    />
                </div>
            </div>

            {/* Analyze Button */}
            <button
                onClick={handleAnalyze}
                disabled={loading || !resumeText || !jobDescription}
                className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50"
            >
                {loading ? (
                    <>
                        <Loader2 className="animate-spin" size={20} />
                        Analyzing with Ollama...
                    </>
                ) : (
                    <>
                        <Target size={20} />
                        Analyze Match
                    </>
                )}
            </button>

            {/* Results */}
            {result && !loading && (
                <div className="space-y-6">
                    {/* Score Cards */}
                    <div className="grid md:grid-cols-3 gap-6">
                        {/* Overall Score */}
                        <div className="card p-6 text-center">
                            <div className="text-sm text-sand-400 mb-2">Overall Match</div>
                            <div className={`text-5xl font-bold ${getScoreColor(result.overallScore)}`}>
                                {result.overallScore}%
                            </div>
                            <div className="mt-3 h-2 bg-[#252530] rounded-full overflow-hidden">
                                <div
                                    className={`h-full ${getScoreBg(result.overallScore)} transition-all duration-500`}
                                    style={{ width: `${result.overallScore}%` }}
                                />
                            </div>
                        </div>

                        {/* Keyword Match */}
                        <div className="card p-6 text-center">
                            <div className="text-sm text-sand-400 mb-2">Keyword Match</div>
                            <div className={`text-5xl font-bold ${getScoreColor(result.keywordMatch)}`}>
                                {result.keywordMatch}%
                            </div>
                            <div className="mt-3 h-2 bg-[#252530] rounded-full overflow-hidden">
                                <div
                                    className={`h-full ${getScoreBg(result.keywordMatch)} transition-all duration-500`}
                                    style={{ width: `${result.keywordMatch}%` }}
                                />
                            </div>
                        </div>

                        {/* ATS Compatibility */}
                        <div className="card p-6 text-center">
                            <div className="text-sm text-sand-400 mb-2">ATS Compatibility</div>
                            <div className={`text-5xl font-bold ${getScoreColor(result.atsCompatibility)}`}>
                                {result.atsCompatibility}%
                            </div>
                            <div className="mt-3 h-2 bg-[#252530] rounded-full overflow-hidden">
                                <div
                                    className={`h-full ${getScoreBg(result.atsCompatibility)} transition-all duration-500`}
                                    style={{ width: `${result.atsCompatibility}%` }}
                                />
                            </div>
                        </div>
                    </div>

                    {/* Keywords Analysis */}
                    <div className="grid md:grid-cols-2 gap-6">
                        {/* Matched Keywords */}
                        <div className="card p-6">
                            <div className="flex items-center gap-2 mb-4">
                                <CheckCircle className="text-emerald-400" size={20} />
                                <h3 className="font-semibold">Matched Keywords</h3>
                            </div>
                            <div className="flex flex-wrap gap-2">
                                {result.matchedKeywords.map((keyword) => (
                                    <span
                                        key={keyword}
                                        className="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-400 text-sm"
                                    >
                                        {keyword}
                                    </span>
                                ))}
                            </div>
                        </div>

                        {/* Missing Keywords */}
                        <div className="card p-6">
                            <div className="flex items-center gap-2 mb-4">
                                <AlertCircle className="text-amber-400" size={20} />
                                <h3 className="font-semibold">Missing Keywords</h3>
                            </div>
                            <div className="flex flex-wrap gap-2">
                                {result.missingKeywords.map((keyword) => (
                                    <span
                                        key={keyword}
                                        className="px-3 py-1 rounded-full bg-amber-500/20 text-amber-400 text-sm"
                                    >
                                        {keyword}
                                    </span>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Suggestions */}
                    <div className="card p-6">
                        <div className="flex items-center gap-2 mb-4">
                            <Lightbulb className="text-electric-400" size={20} />
                            <h3 className="font-semibold">Improvement Suggestions</h3>
                        </div>
                        <ul className="space-y-3">
                            {result.suggestions.map((suggestion, idx) => (
                                <li key={idx} className="flex items-start gap-3">
                                    <div className="w-6 h-6 rounded-full bg-electric-500/20 text-electric-400 flex items-center justify-center text-xs font-medium flex-shrink-0 mt-0.5">
                                        {idx + 1}
                                    </div>
                                    <span className="text-sand-300">{suggestion}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>
            )}

            {/* How it works */}
            {!result && !loading && (
                <div className="card p-8">
                    <h2 className="font-display text-xl font-bold mb-6">How Resume Matcher Works</h2>
                    <div className="grid md:grid-cols-3 gap-6">
                        <div className="p-4 rounded-xl bg-[#252530]/50">
                            <div className="text-2xl mb-3">🔒</div>
                            <h3 className="font-semibold mb-2">Local Processing</h3>
                            <p className="text-sm text-sand-400">
                                Uses Ollama to run AI models locally. Your data never leaves your machine.
                            </p>
                        </div>
                        <div className="p-4 rounded-xl bg-[#252530]/50">
                            <div className="text-2xl mb-3">🎯</div>
                            <h3 className="font-semibold mb-2">Keyword Analysis</h3>
                            <p className="text-sm text-sand-400">
                                Identifies matched and missing keywords to optimize your resume.
                            </p>
                        </div>
                        <div className="p-4 rounded-xl bg-[#252530]/50">
                            <div className="text-2xl mb-3">📊</div>
                            <h3 className="font-semibold mb-2">ATS Scoring</h3>
                            <p className="text-sm text-sand-400">
                                Analyzes format, structure, and content for ATS compatibility.
                            </p>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}

