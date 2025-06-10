"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Play, Download, Share, Clock, Eye } from "lucide-react"

interface Animation {
  id: string
  title: string
  prompt: string
  status: "completed" | "processing" | "failed"
  createdAt: string
  duration: number
  views: number
  videoUrl?: string
  thumbnailUrl?: string
}

export function AnimationHistory() {
  const [animations, setAnimations] = useState<Animation[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Simulate loading animations from API
    setTimeout(() => {
      setAnimations([
        {
          id: "1",
          title: "Pythagorean Theorem Visualization",
          prompt: "Create a visualization of the Pythagorean theorem with animated squares",
          status: "completed",
          createdAt: "2024-01-15T10:30:00Z",
          duration: 45,
          views: 127,
          videoUrl: "/placeholder-video.mp4",
          thumbnailUrl: "/placeholder.svg?height=200&width=300",
        },
        {
          id: "2",
          title: "Fourier Series Animation",
          prompt: "Animate the construction of a square wave using Fourier series",
          status: "processing",
          createdAt: "2024-01-15T11:15:00Z",
          duration: 0,
          views: 0,
        },
        {
          id: "3",
          title: "3D Function Plotting",
          prompt: "Create a 3D plot of z = sin(x) * cos(y) with rotating camera",
          status: "completed",
          createdAt: "2024-01-14T16:45:00Z",
          duration: 60,
          views: 89,
          videoUrl: "/placeholder-video.mp4",
          thumbnailUrl: "/placeholder.svg?height=200&width=300",
        },
      ])
      setIsLoading(false)
    }, 1000)
  }, [])

  const getStatusColor = (status: Animation["status"]) => {
    switch (status) {
      case "completed":
        return "bg-green-500/20 text-green-400 border-green-500/30"
      case "processing":
        return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30"
      case "failed":
        return "bg-red-500/20 text-red-400 border-red-500/30"
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  if (isLoading) {
    return (
      <section className="container mx-auto px-4 py-16">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-blue-500/30 border-t-blue-500 rounded-full animate-spin mx-auto" />
          <p className="text-slate-400 mt-4">Loading your animations...</p>
        </div>
      </section>
    )
  }

  return (
    <section className="container mx-auto px-4 py-16">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <h2 className="text-3xl font-bold text-white mb-2">Your Animations</h2>
        <p className="text-slate-400">Manage and share your mathematical animations</p>
      </motion.div>

      <div className="grid gap-6">
        {animations.map((animation, index) => (
          <motion.div
            key={animation.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Card className="bg-slate-900/50 border-blue-900/30 backdrop-blur-sm p-6 hover:bg-slate-900/70 transition-colors">
              <div className="flex flex-col lg:flex-row gap-6">
                {/* Thumbnail */}
                <div className="lg:w-80 flex-shrink-0">
                  <div className="aspect-video bg-slate-800 rounded-lg overflow-hidden relative">
                    {animation.thumbnailUrl ? (
                      <img
                        src={animation.thumbnailUrl || "/placeholder.svg"}
                        alt={animation.title}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center">
                        <div className="w-8 h-8 border-2 border-blue-500/30 border-t-blue-500 rounded-full animate-spin" />
                      </div>
                    )}
                    {animation.status === "completed" && (
                      <div className="absolute inset-0 flex items-center justify-center bg-black/50 opacity-0 hover:opacity-100 transition-opacity">
                        <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
                          <Play className="w-4 h-4 mr-2" />
                          Play
                        </Button>
                      </div>
                    )}
                  </div>
                </div>

                {/* Content */}
                <div className="flex-1 space-y-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="text-xl font-semibold text-white mb-2">{animation.title}</h3>
                      <p className="text-slate-300 text-sm leading-relaxed">{animation.prompt}</p>
                    </div>
                    <Badge className={getStatusColor(animation.status)}>{animation.status}</Badge>
                  </div>

                  <div className="flex items-center space-x-6 text-sm text-slate-400">
                    <div className="flex items-center space-x-1">
                      <Clock className="w-4 h-4" />
                      <span>{formatDate(animation.createdAt)}</span>
                    </div>
                    {animation.duration > 0 && (
                      <div className="flex items-center space-x-1">
                        <Play className="w-4 h-4" />
                        <span>{animation.duration}s</span>
                      </div>
                    )}
                    <div className="flex items-center space-x-1">
                      <Eye className="w-4 h-4" />
                      <span>{animation.views} views</span>
                    </div>
                  </div>

                  {animation.status === "completed" && (
                    <div className="flex space-x-3">
                      <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
                        <Play className="w-4 h-4 mr-2" />
                        Watch
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        className="border-blue-700/30 text-blue-300 hover:bg-blue-900/20"
                      >
                        <Download className="w-4 h-4 mr-2" />
                        Download
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        className="border-blue-700/30 text-blue-300 hover:bg-blue-900/20"
                      >
                        <Share className="w-4 h-4 mr-2" />
                        Share
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            </Card>
          </motion.div>
        ))}
      </div>
    </section>
  )
}
