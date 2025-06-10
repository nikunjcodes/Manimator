// Database Models for MongoDB

export interface User {
  _id?: string
  email: string
  password: string
  name: string
  createdAt: Date
  updatedAt: Date
  isActive: boolean
  subscription?: "free" | "pro" | "enterprise"
}

export interface Animation {
  _id?: string
  userId: string
  title: string
  prompt: string
  description?: string
  status: "pending" | "processing" | "completed" | "failed"
  manimCode?: string
  videoUrl?: string
  thumbnailUrl?: string
  duration?: number
  views: number
  isPublic: boolean
  tags: string[]
  createdAt: Date
  updatedAt: Date
  processingStartedAt?: Date
  processingCompletedAt?: Date
  errorMessage?: string
}

export interface ChatHistory {
  _id?: string
  userId: string
  animationId?: string
  messages: ChatMessage[]
  createdAt: Date
  updatedAt: Date
}

export interface ChatMessage {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
  metadata?: {
    prompt?: string
    generatedCode?: string
    suggestions?: string[]
  }
}

export interface ApiKey {
  _id?: string
  userId: string
  name: string
  key: string
  isActive: boolean
  lastUsed?: Date
  createdAt: Date
  expiresAt?: Date
}

export interface Usage {
  _id?: string
  userId: string
  date: Date
  animationsGenerated: number
  processingTimeMinutes: number
  storageUsedMB: number
}
