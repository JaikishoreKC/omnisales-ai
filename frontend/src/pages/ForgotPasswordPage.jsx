import React, { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { requestPasswordReset, resetPassword } from '../services/api'

const ForgotPasswordPage = () => {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const token = searchParams.get('token')

  const [email, setEmail] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [loading, setLoading] = useState(false)
  const [resetToken, setResetToken] = useState(token || '')

  const handleRequestReset = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const data = await requestPasswordReset({ email })

      // For demo purposes, since we're not sending emails yet
      if (data.token) {
        setResetToken(data.token)
        setSuccess(true)
      } else {
        setSuccess(true)
      }

    } catch (err) {
      setError(err.message || 'Failed to request password reset')
    } finally {
      setLoading(false)
    }
  }

  const handleResetPassword = async (e) => {
    e.preventDefault()
    setError('')

    if (newPassword.length < 6) {
      setError('Password must be at least 6 characters')
      return
    }

    if (newPassword !== confirmPassword) {
      setError('Passwords do not match')
      return
    }

    setLoading(true)

    try {
      await resetPassword({
        token: resetToken,
        new_password: newPassword
      })

      setSuccess(true)
      
      // Redirect to login after 2 seconds
      setTimeout(() => {
        navigate('/login')
      }, 2000)

    } catch (err) {
      setError(err.message || 'Failed to reset password')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-xl p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {resetToken ? 'Reset Password' : 'Forgot Password'}
          </h1>
          <p className="text-gray-600">
            {resetToken 
              ? 'Enter your new password below'
              : 'Enter your email to receive a reset link'
            }
          </p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}

        {success && !resetToken && (
          <div className="mb-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded">
            <p className="font-semibold mb-2">✓ Reset link sent!</p>
            <p className="text-sm">
              If the email exists, a reset link has been sent. 
              {/* For demo purposes only */}
              <br/><br/>
              <strong>Demo Mode:</strong> Copy this token and use it below:
              <br/>
              <code className="bg-gray-100 px-2 py-1 rounded text-xs break-all block mt-2">
                {resetToken}
              </code>
            </p>
          </div>
        )}

        {success && resetToken && (
          <div className="mb-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded">
            ✓ Password reset successfully! Redirecting to login...
          </div>
        )}

        {!resetToken ? (
          // Request Reset Form
          <form onSubmit={handleRequestReset} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter your email"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition"
            >
              {loading ? 'Sending...' : 'Send Reset Link'}
            </button>
          </form>
        ) : (
          // Reset Password Form
          <form onSubmit={handleResetPassword} className="space-y-4">
            {!token && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Reset Token
                </label>
                <textarea
                  value={resetToken}
                  onChange={(e) => setResetToken(e.target.value)}
                  required
                  rows={3}
                  className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-xs font-mono"
                  placeholder="Paste your reset token here"
                />
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                New Password
              </label>
              <input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
                minLength={6}
                className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter new password (min 6 characters)"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Confirm Password
              </label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                minLength={6}
                className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Confirm new password"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition"
            >
              {loading ? 'Resetting...' : 'Reset Password'}
            </button>
          </form>
        )}

        <div className="mt-6 text-center space-y-2">
          <Link
            to="/login"
            className="block text-blue-600 hover:underline text-sm"
          >
            ← Back to Login
          </Link>
          <Link
            to="/register"
            className="block text-gray-600 hover:underline text-sm"
          >
            Don&apos;t have an account? Register
          </Link>
        </div>

        {!resetToken && (
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <p className="text-xs text-gray-600">
              <strong>Note:</strong> For security, we&apos;ll send a password reset link to your email if an account exists. 
              The link expires in 1 hour.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default ForgotPasswordPage
