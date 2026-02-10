import React, { useState } from 'react'
import AnalyticsDashboard from '../components/AnalyticsDashboard'

const AnalyticsPage = () => {
  return (
    <div className="px-4 py-6">
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Sales Analytics</h2>
          <AnalyticsDashboard />
        </div>
      </div>
    </div>
  )
}

export default AnalyticsPage
