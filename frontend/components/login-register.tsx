"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Label } from "@/components/ui/label"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Brain, Loader2 } from "lucide-react"

interface LoginRegisterProps {
  onLogin: (token: string) => void
}

export function LoginRegister({ onLogin }: LoginRegisterProps) {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")

  const handleAuth = async (isLogin: boolean) => {
    if (!email || !password) {
      setError("Please fill in all fields")
      return
    }

    setIsLoading(true)
    setError("")

    try {
      const endpoint = isLogin ? "/auth/login" : "/auth/register"
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}${endpoint}?email=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`,
        {
          method: "POST",
        },
      )

      if (!response.ok) {
        throw new Error("Authentication failed")
      }

      const data = await response.json()
      onLogin(data.access_token)
    } catch (err) {
      setError(isLogin ? "Login failed. Please check your credentials." : "Registration failed. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <Brain className="h-12 w-12 text-blue-400" />
          </div>
          <h1 className="text-4xl font-bold text-white mb-2">StudyAI</h1>
          <p className="text-slate-300">Your intelligent document companion</p>
        </div>

        <Card className="bg-white/10 backdrop-blur-lg border-white/20 shadow-2xl">
          <CardHeader>
            <CardTitle className="text-white text-2xl text-center">Welcome Back</CardTitle>
            <CardDescription className="text-slate-300 text-center">
              Sign in to your account or create a new one
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="login" className="w-full">
              <TabsList className="grid w-full grid-cols-2 bg-white/10 backdrop-blur">
                <TabsTrigger
                  value="login"
                  className="text-slate-300 data-[state=active]:text-white data-[state=active]:bg-white/20"
                >
                  Sign In
                </TabsTrigger>
                <TabsTrigger
                  value="register"
                  className="text-slate-300 data-[state=active]:text-white data-[state=active]:bg-white/20"
                >
                  Sign Up
                </TabsTrigger>
              </TabsList>

              <TabsContent value="login" className="space-y-4 mt-6">
                <div className="space-y-2">
                  <Label htmlFor="email" className="text-white font-medium">
                    Email Address
                  </Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="Enter your email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="bg-white/10 border-white/20 text-white placeholder:text-slate-400 focus:border-blue-400 focus:ring-blue-400"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="password" className="text-white font-medium">
                    Password
                  </Label>
                  <Input
                    id="password"
                    type="password"
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="bg-white/10 border-white/20 text-white placeholder:text-slate-400 focus:border-blue-400 focus:ring-blue-400"
                  />
                </div>
                {error && (
                  <Alert className="bg-red-500/20 border-red-400/50 backdrop-blur">
                    <AlertDescription className="text-red-200">{error}</AlertDescription>
                  </Alert>
                )}
                <Button
                  onClick={() => handleAuth(true)}
                  disabled={isLoading}
                  className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold py-3 rounded-lg transition-all duration-200 shadow-lg"
                >
                  {isLoading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                  Sign In
                </Button>
              </TabsContent>

              <TabsContent value="register" className="space-y-4 mt-6">
                <div className="space-y-2">
                  <Label htmlFor="reg-email" className="text-white font-medium">
                    Email Address
                  </Label>
                  <Input
                    id="reg-email"
                    type="email"
                    placeholder="Enter your email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="bg-white/10 border-white/20 text-white placeholder:text-slate-400 focus:border-blue-400 focus:ring-blue-400"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="reg-password" className="text-white font-medium">
                    Password
                  </Label>
                  <Input
                    id="reg-password"
                    type="password"
                    placeholder="Create a password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="bg-white/10 border-white/20 text-white placeholder:text-slate-400 focus:border-blue-400 focus:ring-blue-400"
                  />
                </div>
                {error && (
                  <Alert className="bg-red-500/20 border-red-400/50 backdrop-blur">
                    <AlertDescription className="text-red-200">{error}</AlertDescription>
                  </Alert>
                )}
                <Button
                  onClick={() => handleAuth(false)}
                  disabled={isLoading}
                  className="w-full bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 text-white font-semibold py-3 rounded-lg transition-all duration-200 shadow-lg"
                >
                  {isLoading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                  Create Account
                </Button>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
