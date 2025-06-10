"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Play, Eye, Heart, Share } from "lucide-react"

export function AnimationShowcase() {
  const [selectedCategory, setSelectedCategory] = useState("All")

  const categories = ["All", "Calculus", "Algebra", "Geometry", "Statistics", "Physics"]

  const animations = [
    {
      id: 1,
      title: "Pythagorean Theorem Proof",
      category: "Geometry",
      description: "Visual proof of the Pythagorean theorem using animated squares",
      thumbnail: "/placeholder.svg?height=300&width=400",
      duration: "45s",
      views: 1234,
      likes: 89,
      tags: ["geometry", "proof", "theorem"],
    },
    {
      id: 2,
      title: "Fourier Series Visualization",
      category: "Calculus",
      description: "Building complex waveforms from simple sine waves",
      thumbnail: "/placeholder.svg?height=300&width=400",
      duration: "1m 20s",
      views: 2156,
      likes: 156,
      tags: ["fourier", "series", "waves"],
    },
    {
      id: 3,
      title: "3D Function Plotting",
      category: "Calculus",
      description: "Interactive 3D visualization of multivariable functions",
      thumbnail: "/placeholder.svg?height=300&width=400",
      duration: "2m 15s",
      views: 987,
      likes: 67,
      tags: ["3d", "functions", "calculus"],
    },
    {
      id: 4,
      title: "Matrix Transformations",
      category: "Algebra",
      description: "Visualizing linear transformations in 2D space",
      thumbnail: "/placeholder.svg?height=300&width=400",
      duration: "1m 45s",
      views: 1567,
      likes: 123,
      tags: ["matrix", "linear", "transformation"],
    },
    {
      id: 5,
      title: "Normal Distribution",
      category: "Statistics",
      description: "Understanding the bell curve and its properties",
      thumbnail: "/placeholder.svg?height=300&width=400",
      duration: "1m 30s",
      views: 2234,
      likes: 178,
      tags: ["statistics", "normal", "distribution"],
    },
    {
      id: 6,
      title: "Pendulum Motion",
      category: "Physics",
      description: "Simple harmonic motion and energy conservation",
      thumbnail: "/placeholder.svg?height=300&width=400",
      duration: "2m 5s",
      views: 1456,
      likes: 98,
      tags: ["physics", "pendulum", "motion"],
    },
  ]

  const filteredAnimations =
    selectedCategory === "All" ? animations : animations.filter((anim) => anim.category === selectedCategory)

  return (
    <section id="showcase" className="py-24 px-4 bg-slate-900/30">
      <div className="container mx-auto max-w-7xl">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Animation
            <span className="bg-gradient-to-r from-blue-400 to-blue-600 bg-clip-text text-transparent"> Showcase</span>
          </h2>
          <p className="text-xl text-slate-300 max-w-3xl mx-auto mb-12">
            Explore our gallery of mathematical animations created by our community of educators and students.
          </p>

          {/* Category Filter */}
          <div className="flex flex-wrap justify-center gap-3 mb-12">
            {categories.map((category) => (
              <Button
                key={category}
                variant={selectedCategory === category ? "default" : "outline"}
                onClick={() => setSelectedCategory(category)}
                className={
                  selectedCategory === category
                    ? "bg-blue-600 hover:bg-blue-700 text-white"
                    : "border-blue-500/30 text-blue-300 hover:bg-blue-500/10"
                }
              >
                {category}
              </Button>
            ))}
          </div>
        </motion.div>

        <AnimatePresence mode="wait">
          <motion.div
            key={selectedCategory}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.5 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
          >
            {filteredAnimations.map((animation, index) => (
              <motion.div
                key={animation.id}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
              >
                <Card className="bg-slate-900/50 border-blue-900/30 backdrop-blur-sm overflow-hidden hover:bg-slate-900/70 transition-all duration-300 group">
                  <div className="relative">
                    <img
                      src={animation.thumbnail || "/placeholder.svg"}
                      alt={animation.title}
                      className="w-full h-48 object-cover"
                    />
                    <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center">
                      <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
                        <Play className="w-4 h-4 mr-2" />
                        Play
                      </Button>
                    </div>
                    <Badge className="absolute top-3 right-3 bg-blue-600/90 text-white">{animation.duration}</Badge>
                  </div>

                  <div className="p-6">
                    <div className="flex items-start justify-between mb-3">
                      <h3 className="text-xl font-bold text-white group-hover:text-blue-300 transition-colors">
                        {animation.title}
                      </h3>
                      <Badge variant="outline" className="border-blue-500/30 text-blue-400 text-xs">
                        {animation.category}
                      </Badge>
                    </div>

                    <p className="text-slate-300 text-sm mb-4 leading-relaxed">{animation.description}</p>

                    <div className="flex items-center justify-between text-sm text-slate-400 mb-4">
                      <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-1">
                          <Eye className="w-4 h-4" />
                          <span>{animation.views.toLocaleString()}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Heart className="w-4 h-4" />
                          <span>{animation.likes}</span>
                        </div>
                      </div>
                      <Button size="sm" variant="ghost" className="text-slate-400 hover:text-blue-400">
                        <Share className="w-4 h-4" />
                      </Button>
                    </div>

                    <div className="flex flex-wrap gap-2">
                      {animation.tags.map((tag) => (
                        <Badge key={tag} variant="secondary" className="bg-blue-500/10 text-blue-400 text-xs">
                          #{tag}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </Card>
              </motion.div>
            ))}
          </motion.div>
        </AnimatePresence>
      </div>
    </section>
  )
}
