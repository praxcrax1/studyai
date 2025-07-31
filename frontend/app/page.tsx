"use client"

import { useState, useEffect } from "react"
import { LoginRegister } from "@/components/login-register"
import { Dashboard } from "@/components/dashboard"

export default function Home() {
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const savedToken = localStorage.getItem("studyai_token")
    if (savedToken) {
      setToken(savedToken)
    }
    setIsLoading(false)
  }, [])

  const handleLogin = (newToken: string) => {
    localStorage.setItem("studyai_token", newToken)
    setToken(newToken)
  }

  const handleLogout = () => {
    localStorage.removeItem("studyai_token")
    setToken(null)
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400"></div>
      </div>
    )
  }

  if (!token) {
    return <LoginRegister onLogin={handleLogin} />
  }

  return <Dashboard token={token} onLogout={handleLogout} />
}
