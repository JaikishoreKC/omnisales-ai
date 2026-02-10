import React, { useState } from 'react'
import { analyzeData } from '../services/api'

const AnalyticsDashboard = () => {
  const [query, setQuery] = useState('')
  const [insights, setInsights] = useState('')
  const [loading, setLoading] = useState(false)

  const sampleData = [
    { month: 'Jan', sales: 45000, leads: 120 },
    { month: 'Feb', sales: 52000, leads: 145 },
    { month: 'Mar', sales: 48000, leads: 130 },
    { month: 'Apr', sales: 61000, leads: 160 },
    { month: 'May', sales: 55000, leads: 140 }
  ]

  const handleAnalyze = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    try {
      const response = await analyzeData({
        query: query,
        data: sampleData,
        user_id: 'user123'
      })
      setInsights(response.insights)
    } catch (error) {
      console.error('Error analyzing data:', error)
      setInsights('Error analyzing data. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-3">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <dt className="text-sm font-medium text-gray-500 truncate">Total Sales</dt>
            <dd className="mt-1 text-3xl font-semibold text-gray-900">$261,000</dd>
          </div>
        </div>
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <dt className="text-sm font-medium text-gray-500 truncate">Total Leads</dt>
            <dd className="mt-1 text-3xl font-semibold text-gray-900">695</dd>
          </div>
        </div>
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <dt className="text-sm font-medium text-gray-500 truncate">Avg Monthly</dt>
            <dd className="mt-1 text-3xl font-semibold text-gray-900">$52,200</dd>
          </div>
        </div>
      </div>

      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">AI Analytics</h3>
        <form onSubmit={handleAnalyze} className="space-y-4">
          <div>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask a question about your sales data..."
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows="3"
              disabled={loading}
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
          >
            {loading ? 'Analyzing...' : 'Analyze'}
          </button>
        </form>

        {insights && (
          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            <h4 className="font-medium text-gray-900 mb-2">Insights:</h4>
            <p className="text-gray-700 whitespace-pre-wrap">{insights}</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default AnalyticsDashboard
