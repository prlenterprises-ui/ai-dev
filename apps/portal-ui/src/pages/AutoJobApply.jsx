import { useState } from 'react';
import { Loader2, Search, FileText, Send, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

interface JobApplication {
  id: number;
  job_title: string;
  company: string;
  status: string;
  match_score: number;
  resume_url: string;
  cover_letter_url: string;
  job_url: string;
  created_at: string;
}

interface PipelineUpdate {
  stage: string;
  status: string;
  message: string;
  data?: any;
  error?: string;
}

export default function AutoJobApply() {
  const [keywords, setKeywords] = useState('');
  const [location, setLocation] = useState('');
  const [maxApplications, setMaxApplications] = useState(10);
  const [autoApply, setAutoApply] = useState(false);
  
  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentMessage, setCurrentMessage] = useState('');
  const [updates, setUpdates] = useState<PipelineUpdate[]>([]);
  const [applications, setApplications] = useState<JobApplication[]>([]);
  const [error, setError] = useState('');

  const startPipeline = async () => {
    if (!keywords.trim()) {
      setError('Please enter job keywords');
      return;
    }

    setIsRunning(true);
    setError('');
    setUpdates([]);
    setProgress(0);
    setCurrentMessage('Starting job search...');

    try {
      // Start the pipeline
      const response = await fetch('/api/jobs/auto-apply', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          keywords,
          location: location || null,
          max_applications: maxApplications,
          auto_apply: autoApply
        })
      });

      if (!response.ok) {
        throw new Error('Failed to start pipeline');
      }

      const data = await response.json();
      const pipelineId = data.pipeline_id;

      // Connect to SSE stream for progress updates
      const eventSource = new EventSource(
        `/api/stream/auto-apply/${pipelineId}?keywords=${encodeURIComponent(keywords)}&location=${encodeURIComponent(location || '')}&max_applications=${maxApplications}&auto_apply=${autoApply}`
      );

      eventSource.onmessage = (event) => {
        const update: PipelineUpdate = JSON.parse(event.data);
        
        setUpdates(prev => [...prev, update]);
        setCurrentMessage(update.message);

        // Calculate progress
        const stageProgress: Record<string, number> = {
          'search': 10,
          'filter': 20,
          'processing': 30,
          'generating': 60,
          'generated': 80,
          'applying': 90,
          'pipeline': 100
        };
        
        const progressValue = stageProgress[update.stage] || 0;
        setProgress(progressValue);

        // Handle completion
        if (update.stage === 'pipeline' && update.status === 'completed') {
          eventSource.close();
          setIsRunning(false);
          setProgress(100);
          loadApplications();
        }

        // Handle errors
        if (update.status === 'failed') {
          eventSource.close();
          setIsRunning(false);
          setError(update.error || 'Pipeline failed');
        }
      };

      eventSource.onerror = () => {
        eventSource.close();
        setIsRunning(false);
        setError('Connection lost. Please try again.');
      };

    } catch (err: any) {
      setError(err.message || 'Failed to start pipeline');
      setIsRunning(false);
    }
  };

  const loadApplications = async () => {
    try {
      const response = await fetch('/api/jobs/applications?status=completed&limit=50');
      if (response.ok) {
        const data = await response.json();
        setApplications(data.applications);
      }
    } catch (err) {
      console.error('Failed to load applications:', err);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-400" />;
      case 'started':
        return <Loader2 className="w-4 h-4 animate-spin text-blue-400" />;
      default:
        return <AlertCircle className="w-4 h-4 text-gray-400" />;
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center space-y-3">
        <h1 className="font-display text-4xl font-bold bg-gradient-to-r from-electric-400 to-coral-400 bg-clip-text text-transparent">
          Automated Job Application
        </h1>
        <p className="text-sand-400 text-lg">
          Search, analyze, and apply to jobs automatically with AI-powered resume tailoring
        </p>
      </div>

      {/* Settings Card */}
      <div className="bg-[#1a1a24] rounded-xl border border-[#2a2a35] p-6 space-y-6">
        <div>
          <h2 className="text-xl font-semibold mb-1">Job Search Settings</h2>
          <p className="text-sand-400 text-sm">Configure your automated job application preferences</p>
        </div>
        
        <div className="space-y-4">
          <div className="space-y-2">
            <label className="block text-sm font-medium">Job Keywords *</label>
            <input
              type="text"
              placeholder="e.g., Senior Software Engineer, Python, React"
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
              disabled={isRunning}
              className="w-full px-4 py-2 bg-[#0f0f12] border border-[#2a2a35] rounded-lg focus:outline-none focus:ring-2 focus:ring-electric-500 disabled:opacity-50"
            />
            <p className="text-sm text-sand-500">Enter job titles, skills, or keywords to search for</p>
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium">Location (Optional)</label>
            <input
              type="text"
              placeholder="e.g., San Francisco, Remote, New York"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              disabled={isRunning}
              className="w-full px-4 py-2 bg-[#0f0f12] border border-[#2a2a35] rounded-lg focus:outline-none focus:ring-2 focus:ring-electric-500 disabled:opacity-50"
            />
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium">Maximum Applications</label>
            <input
              type="number"
              min="1"
              max="50"
              value={maxApplications}
              onChange={(e) => setMaxApplications(parseInt(e.target.value) || 10)}
              disabled={isRunning}
              className="w-full px-4 py-2 bg-[#0f0f12] border border-[#2a2a35] rounded-lg focus:outline-none focus:ring-2 focus:ring-electric-500 disabled:opacity-50"
            />
            <p className="text-sm text-sand-500">Number of job applications to generate (1-50)</p>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="auto-apply"
              checked={autoApply}
              onChange={(e) => setAutoApply(e.target.checked)}
              disabled={isRunning}
              className="w-4 h-4 rounded border-[#2a2a35] bg-[#0f0f12] text-electric-500 focus:ring-electric-500"
            />
            <label htmlFor="auto-apply" className="text-sm cursor-pointer">
              Automatically submit applications (when possible)
            </label>
          </div>

          {error && (
            <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400">
              {error}
            </div>
          )}
        </div>

        <button
          onClick={startPipeline}
          disabled={isRunning || !keywords.trim()}
          className="w-full py-3 px-6 bg-gradient-to-r from-electric-500 to-electric-600 hover:from-electric-600 hover:to-electric-700 rounded-lg font-medium flex items-center justify-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isRunning ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Processing...
            </>
          ) : (
            <>
              <Search className="w-5 h-5" />
              Start Auto-Apply
            </>
          )}
        </button>
      </div>

      {/* Progress */}
      {isRunning && (
        <div className="bg-[#1a1a24] rounded-xl border border-[#2a2a35] p-6 space-y-4">
          <div>
            <h3 className="font-semibold mb-1">Pipeline Progress</h3>
            <p className="text-sm text-sand-400">{currentMessage}</p>
          </div>
          <div className="w-full bg-[#0f0f12] rounded-full h-2">
            <div
              className="bg-gradient-to-r from-electric-500 to-electric-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Updates Log */}
      {updates.length > 0 && (
        <div className="bg-[#1a1a24] rounded-xl border border-[#2a2a35] p-6 space-y-4">
          <h3 className="font-semibold">Activity Log</h3>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {updates.map((update, idx) => (
              <div key={idx} className="flex items-start gap-3 p-3 bg-[#0f0f12]/50 rounded-lg">
                {getStatusIcon(update.status)}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="inline-block px-2 py-0.5 bg-electric-500/20 text-electric-400 text-xs rounded-full capitalize">
                      {update.stage}
                    </span>
                    <span className="text-sm text-sand-500 capitalize">{update.status}</span>
                  </div>
                  <p className="text-sm mt-1">{update.message}</p>
                  {update.error && (
                    <p className="text-sm text-red-400 mt-1">{update.error}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Generated Applications */}
      {applications.length > 0 && (
        <div className="bg-[#1a1a24] rounded-xl border border-[#2a2a35] p-6 space-y-4">
          <div>
            <h3 className="font-semibold mb-1">Generated Applications</h3>
            <p className="text-sm text-sand-400">
              {applications.length} applications with tailored resumes and cover letters
            </p>
          </div>
          <div className="space-y-3">
            {applications.map((app) => (
              <div key={app.id} className="flex items-center justify-between p-4 bg-[#0f0f12]/50 rounded-lg border border-[#2a2a35]">
                <div className="flex-1">
                  <h4 className="font-semibold">{app.job_title}</h4>
                  <p className="text-sm text-sand-400">{app.company}</p>
                  {app.match_score && (
                    <span className="inline-block mt-1 px-2 py-0.5 bg-green-500/20 text-green-400 text-xs rounded-full">
                      {app.match_score}% Match
                    </span>
                  )}
                </div>
                <div className="flex gap-2">
                  {app.resume_url && (
                    <a
                      href={app.resume_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-3 py-2 bg-[#1a1a24] border border-[#2a2a35] rounded-lg text-sm flex items-center gap-1 hover:bg-[#2a2a35] transition-colors"
                    >
                      <FileText className="w-4 h-4" />
                      Resume
                    </a>
                  )}
                  {app.cover_letter_url && (
                    <a
                      href={app.cover_letter_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-3 py-2 bg-[#1a1a24] border border-[#2a2a35] rounded-lg text-sm flex items-center gap-1 hover:bg-[#2a2a35] transition-colors"
                    >
                      <FileText className="w-4 h-4" />
                      Cover Letter
                    </a>
                  )}
                  {app.job_url && (
                    <a
                      href={app.job_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-3 py-2 bg-electric-500 hover:bg-electric-600 rounded-lg text-sm flex items-center gap-1 transition-colors"
                    >
                      <Send className="w-4 h-4" />
                      Apply
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
