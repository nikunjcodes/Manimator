"use client"

import { createContext, useContext, useState, useEffect, type ReactNode } from "react"

interface User {
  id: string
  email: string
  name: string
}

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, name: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    // Check for existing token on mount
    const token = localStorage.getItem("auth_token")
    if (token) {
      // Validate token and get user data
      validateToken(token)
    }
  }, [])

  const validateToken = async (token: string) => {
    try {
      const response = await fetch("http://localhost:5000/api/auth/validate", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const userData = await response.json()
        setUser(userData)
        setIsAuthenticated(true)
      } else {
        localStorage.removeItem("auth_token")
      }
    } catch (error) {
      console.error("Token validation failed:", error)
      localStorage.removeItem("auth_token")
    }
  }

  const login = async (email: string, password: string) => {
    try {
      console.log("Attempting login with:", { email }) // Debug log
      
      const response = await fetch("http://localhost:5000/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      })

      // Log the raw response for debugging
      console.log("Login response status:", response.status)
      const responseText = await response.text()
      console.log("Raw response:", responseText)

      if (response.ok) {
        try {
          const data = JSON.parse(responseText)
          localStorage.setItem("auth_token", data.access_token)
          setUser(data.user)
          setIsAuthenticated(true)
        } catch (parseError) {
          console.error("Failed to parse successful response:", parseError)
          throw new Error("Invalid server response format")
        }
      } else {
        try {
          const errorData = JSON.parse(responseText)
          throw new Error(errorData.message || "Login failed")
        } catch (parseError) {
          console.error("Failed to parse error response:", parseError)
          throw new Error(`Login failed: ${response.status} ${response.statusText}`)
        }
      }
    } catch (error) {
      console.error("Login error:", error)
      throw error
    }
  }

  const register = async (email: string, password: string, name: string) => {
    try {
      console.log("Attempting registration with:", { email, name , password }) // Debug log
      
      const response = await fetch("http://localhost:5000/api/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password, name }),
      })

      // Log the raw response for debugging
      console.log("Registration response status:", response.status)
      const responseText = await response.text()
      console.log("Raw response:", responseText)

      if (response.ok) {
        try {
          const data = JSON.parse(responseText)
          localStorage.setItem("auth_token", data.access_token)
          setUser(data.user)
          setIsAuthenticated(true)
        } catch (parseError) {
          console.error("Failed to parse successful response:", parseError)
          throw new Error("Invalid server response format")
        }
      } else {
        try {
          const errorData = JSON.parse(responseText)
          throw new Error(errorData.message || "Registration failed")
        } catch (parseError) {
          console.error("Failed to parse error response:", parseError)
          throw new Error(`Registration failed: ${response.status} ${response.statusText}`)
        }
      }
    } catch (error) {
      console.error("Registration error:", error)
      throw error
    }
  }

  const logout = () => {
    localStorage.removeItem("auth_token")
    setUser(null)
    setIsAuthenticated(false)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
