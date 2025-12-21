import { useState, useEffect } from 'react';
import { Loader2, Search, Briefcase, ExternalLink, Calendar, Building2 } from 'lucide-react';

export default function AutoJobApply() {
  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentMessage, setCurrentMessage] = useState('');
  const [applications, setApplications] = useState([]);
  const [error, setError] = useState('');
  const [searchStatus, setSearchStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkSearchStatus();
    loadApplications();
  }, []);

  const checkSearchStatus = async () => {
    try {
      const response = await fetch('/api/jobs/search-availability');
      if (response.ok) {
        const data = await response.json();
        setSearchStatus({
          can_search: data.available,
          hours_until_next: data.hours_until_available,
          last_search: data.last_search_timestamp,
          reason: data.reason
        });
      }
    } catch (err) {
      console.error('Failed to check search status:', err);
    }
  };

  const loadApplications = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/jobs/applications?limit=100');
      if (response.ok) {
        const data = await response.json();
        setApplications(data.applications || []);
      }
    } catch (err) {
      console.error('Failed to load applications:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFindJobs = async () => {
    // Check 24-hour cooldown
    if (searchStatus && !searchStatus.can_search) {
      setError(`Please wait ${searchStatus.hours_until_next.toFixed(1)} hours before searching again (24-hour cooldown)`);
      return;
    }

    setIsRunning(true);
    setError('');
    setProgress(0);
    setCurrentMessage('Starting job search...');

    try {
      // Load config from database
      const configResponse = await fetch('/api/configs/auto-apply');
      if (!configResponse.ok) throw new Error('Failed to load configuration');
      const configData = await configResponse.json();
      const config = configData.config;

      // Start the pipeline with config from database
      const response = await fetch('/api/jobs/auto-apply', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          keywords: config.jsearch.queries.join(', '),
          location: config.jsearch.location || null,
          max_applications: 100,
          auto_apply: false
        })
      });

      if (!response.ok) {
        throw new Error('Failed to start pipeline');
      }

      const data = await response.json();
      const pipelineId = data.pipeline_id;

      // Connect to SSE stream for progress updates
      const eventSource = new EventSource(
        `/api/stream/auto-apply/${pipelineId}?keywords=${encodeURIComponent(config.jsearch.queries.join(', '))}&location=${encodeURIComponent(config.jsearch.location || '')}&max_applications=100&auto_apply=false`
      );

      eventSource.onmessage = (event) => {
        const update = JSON.parse(event.data);
        
        setCurrentMessage(update.message);

        // Calculate progress
        const stageProgress = {
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
          checkSearchStatus(); // Refresh cooldown status
        }

        // Handle rate limiting
        if (update.status === 'rate_limited') {
          eventSource.close();
          setIsRunning(false);
          setError(update.message || update.error || 'Search rate limited. Please wait 24 hours between searches.');
          checkSearchStatus(); // Refresh cooldown status
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

    } catch (err) {
      setError(err.message || 'Failed to start pipeline');
      setIsRunning(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return 'bg-yellow-500/20 text-yellow-300';
      case 'completed': return 'bg-green-500/20 text-green-300';
      case 'applied': return 'bg-blue-500/20 text-blue-300';
      case 'failed': return 'bg-red-500/20 text-red-300';
      default: return 'bg-gray-500/20 text-gray-300';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  return (
    <div className="space-y-8">
      {/* Header with Find Jobs button */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-electric-500 to-electric-600 flex items-center justify-center">
            <Briefcase className="text-white" size={28} />
          </div>
          <div>
            <h1 className="font-display text-3xl font-bold">Automated Job Application</h1>
            <p className="text-sand-400">AI-powered job search with 100-job limit per search</p>
          </div>
        </div>
        
        <button
          onClick={handleFindJobs}
          disabled={isRunning || (searchStatus && !searchStatus.can_search)}
          className="px-6 py-3 bg-gradient-to-r from-electric-500 to-electric-600 hover:from-electric-600 hover:to-electric-700 rounded-lg font-medium flex items-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isRunning ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Processing...
            </>
          ) : (
            <>
              <Search className="w-5 h-5" />
              Find Jobs
            </>
          )}
        </button>
      </div>

      {/* Cooldown Warning */}
      {searchStatus && !searchStatus.can_search && (
        <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-4">
          <p className="font-medium text-yellow-400">⏱️ Search Cooldown Active</p>
          <p className="text-sm text-sand-400 mt-1">
            You can search again in {searchStatus.hours_until_next.toFixed(1)} hours (24-hour rate limit)
          </p>
        </div>
      )}

      {/* Progress */}
      {isRunning && (
        <div className="bg-[#1a1a24] rounded-xl border border-[#2a2a35] p-6">
          <div className="flex items-center gap-3 mb-4">
            <Loader2 className="w-5 h-5 animate-spin text-electric-400" />
            <span className="font-medium">Job Search in Progress</span>
          </div>
          <div className="w-full bg-[#0f0f12] rounded-full h-2 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-electric-500 to-electric-600 transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-sm text-sand-400 mt-2">{currentMessage}</p>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4 text-red-400">
          {error}
        </div>
      )}

      {/* Job Applications Table */}
      <div className="bg-[#1a1a24] rounded-xl border border-[#2a2a35] overflow-hidden">
        <div className="p-6 border-b border-[#2a2a35]">
          <h2 className="text-xl font-semibold">Job Applications</h2>
          <p className="text-sm text-sand-400 mt-1">{applications.length} jobs found</p>
        </div>

        {loading ? (
          <div className="p-12 text-center">
            <Loader2 className="w-8 h-8 animate-spin text-electric-400 mx-auto mb-3" />
            <p className="text-sand-400">Loading applications...</p>
          </div>
        ) : applications.length === 0 ? (
          <div className="p-12 text-center">
            <Briefcase className="w-12 h-12 text-sand-600 mx-auto mb-3" />
            <p className="text-sand-400">No job applications yet. Click "Find Jobs" to start searching.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-[#252530] border-b border-[#2a2a35]">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-sand-400 uppercase tracking-wider">Job Title</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-sand-400 uppercase tracking-wider">Company</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-sand-400 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-sand-400 uppercase tracking-wider">Match Score</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-sand-400 uppercase tracking-wider">Date</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-sand-400 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#2a2a35]">
                {applications.map((app) => (
                  <tr key={app.id} className="hover:bg-[#252530] transition-colors">
                    <td className="px-6 py-4">
                      <div className="font-medium text-white">{app.job_title}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2 text-sand-300">
                        <Building2 className="w-4 h-4 text-sand-500" />
                        {app.company}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(app.status)}`}>
                        {app.status}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      {app.match_score ? (
                        <span className="text-electric-400 font-medium">{Math.round(app.match_score * 100)}%</span>
                      ) : (
                        <span className="text-sand-500">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2 text-sm text-sand-400">
                        <Calendar className="w-4 h-4" />
                        {formatDate(app.created_at)}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        {app.job_url && (
                          <a
                            href={app.job_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-electric-400 hover:text-electric-300 transition-colors"
                            title="View Job"
                          >
                            <ExternalLink className="w-4 h-4" />
                          </a>
                        )}
                        {app.resume_url && (
                          <a
                            href={app.resume_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-sand-400 hover:text-sand-300 transition-colors text-xs px-2 py-1 bg-[#252530] rounded"
                          >
                            Resume
                          </a>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
