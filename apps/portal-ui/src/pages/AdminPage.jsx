import { useState, useEffect } from 'react'
import { Settings, Save, RotateCcw, Plus, Trash2, Edit3 } from 'lucide-react'

const API_URL = '/api/configs/'

export default function AdminPage() {
  const [configs, setConfigs] = useState([])
  const [selectedConfig, setSelectedConfig] = useState(null)
  const [editingConfig, setEditingConfig] = useState(null)
  const [jsonError, setJsonError] = useState(null)
  const [saving, setSaving] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadConfigs()
  }, [])

  const loadConfigs = async () => {
    try {
      setLoading(true)
      const response = await fetch(API_URL)
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      const data = await response.json()
      console.log('Loaded configs:', data)
      setConfigs(data)
    } catch (error) {
      console.error('Error loading configs:', error)
      alert('Failed to load configs: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  const handleConfigClick = (config) => {
    setSelectedConfig(config)
    setEditingConfig({
      ...config,
      configJson: JSON.stringify(config.config, null, 2)
    })
    setJsonError(null)
  }

  const handleJsonChange = (value) => {
    setEditingConfig({ ...editingConfig, configJson: value })
    
    // Validate JSON
    try {
      JSON.parse(value)
      setJsonError(null)
    } catch (e) {
      setJsonError(e.message)
    }
  }

  const handleSave = async () => {
    if (jsonError) return

    try {
      setSaving(true)
      const parsedConfig = JSON.parse(editingConfig.configJson)
      
      const response = await fetch(`${API_URL}/${selectedConfig.name}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: editingConfig.title,
          description: editingConfig.description,
          config_json: parsedConfig
        })
      })

      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      const data = await response.json()
      
      // Update local state
      const updatedConfig = data
      setConfigs(configs.map(c => c.name === updatedConfig.name ? updatedConfig : c))
      setSelectedConfig(updatedConfig)
      setEditingConfig({
        ...updatedConfig,
        configJson: JSON.stringify(updatedConfig.config, null, 2)
      })

      // Show success (you could add a toast notification here)
      alert('Configuration saved successfully!')
    } catch (error) {
      console.error('Error saving config:', error)
      alert('Failed to save configuration: ' + error.message)
    } finally {
      setSaving(false)
    }
  }

  const handleReset = () => {
    if (selectedConfig) {
      setEditingConfig({
        ...selectedConfig,
        configJson: JSON.stringify(selectedConfig.config, null, 2)
      })
      setJsonError(null)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-electric-500 mx-auto mb-4"></div>
          <p className="text-sand-400">Loading configurations...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center gap-4">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-electric-500 to-coral-500 flex items-center justify-center">
          <Settings className="w-6 h-6" />
        </div>
        <div>
          <h1 className="font-display text-3xl font-bold">Admin</h1>
          <p className="text-sand-400">Manage application configurations</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Config Cards List */}
        <div className="lg:col-span-1 space-y-4">
          <h2 className="font-display text-xl font-bold mb-4">Configurations</h2>
          
          {configs.length === 0 ? (
            <div className="glass-card p-6 text-center text-sand-400">
              <p>No configurations found</p>
            </div>
          ) : (
            configs.map((config) => (
              <button
                key={config.name}
                onClick={() => handleConfigClick(config)}
                className={`
                  w-full glass-card p-4 text-left transition-all hover:border-electric-500/50
                  ${selectedConfig?.name === config.name ? 'border-electric-500 bg-electric-500/5' : ''}
                `}
              >
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 rounded-lg bg-electric-500/20 flex items-center justify-center flex-shrink-0">
                    <Settings className="w-5 h-5 text-electric-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold truncate">{config.title}</h3>
                    {config.description && (
                      <p className="text-sm text-sand-400 mt-1 line-clamp-2">
                        {config.description}
                      </p>
                    )}
                    <p className="text-xs text-sand-500 mt-2">
                      Updated: {new Date(config.updated_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              </button>
            ))
          )}
        </div>

        {/* Config Editor */}
        <div className="lg:col-span-2">
          {selectedConfig ? (
            <div className="glass-card p-6 space-y-6">
              {/* Editor Header */}
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="font-display text-xl font-bold">{editingConfig?.title}</h2>
                  <p className="text-sm text-sand-400 mt-1">{editingConfig?.description}</p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={handleReset}
                    disabled={saving}
                    className="flex items-center gap-2 px-4 py-2 rounded-lg border border-[#2a2a35] text-sand-400 hover:text-white hover:border-electric-500/50 transition-all disabled:opacity-50"
                  >
                    <RotateCcw size={16} />
                    Reset
                  </button>
                  <button
                    onClick={handleSave}
                    disabled={!!jsonError || saving}
                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-electric-500 hover:bg-electric-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Save size={16} />
                    {saving ? 'Saving...' : 'Save'}
                  </button>
                </div>
              </div>

              {/* JSON Editor */}
              <div className="space-y-2">
                <label className="block text-sm font-medium text-sand-300">
                  Configuration (JSON)
                </label>
                <div className="relative">
                  <textarea
                    value={editingConfig?.configJson || ''}
                    onChange={(e) => handleJsonChange(e.target.value)}
                    className={`
                      w-full h-[500px] px-4 py-3 bg-[#0a0a0f] border rounded-lg
                      font-mono text-sm text-sand-100
                      focus:outline-none focus:ring-2 focus:ring-electric-500/50
                      ${jsonError ? 'border-red-500' : 'border-[#2a2a35]'}
                    `}
                    spellCheck="false"
                  />
                </div>
                
                {/* Error Message */}
                {jsonError && (
                  <div className="flex items-start gap-2 p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
                    <div className="text-red-400 text-sm">
                      <strong>JSON Error:</strong> {jsonError}
                    </div>
                  </div>
                )}

                {/* Help Text */}
                <p className="text-xs text-sand-500">
                  Edit the JSON configuration above. Changes will be validated in real-time.
                </p>
              </div>

              {/* Metadata */}
              <div className="grid grid-cols-2 gap-4 pt-4 border-t border-[#2a2a35]">
                <div>
                  <p className="text-xs text-sand-500">Created</p>
                  <p className="text-sm text-sand-300">
                    {new Date(selectedConfig.created_at).toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-sand-500">Last Updated</p>
                  <p className="text-sm text-sand-300">
                    {new Date(selectedConfig.updated_at).toLocaleString()}
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="glass-card p-12 text-center">
              <Settings className="w-16 h-16 text-sand-600 mx-auto mb-4" />
              <h3 className="font-display text-xl font-bold mb-2">No Configuration Selected</h3>
              <p className="text-sand-400">
                Select a configuration from the list to view and edit it
              </p>
            </div>
          )}
        </div>
      </div>

    </div>
  )
}
