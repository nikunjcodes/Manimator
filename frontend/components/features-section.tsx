"use client"

import { motion } from "framer-motion"
import { Card } from "@/components/ui/card"
import { Zap, Code, Sparkles, Download, Share, Clock } from "lucide-react"

export function FeaturesSection() {
  const features = [
    {
      icon: Sparkles,
      title: "AI-Powered Generation",
      description:
        "Describe your mathematical concept in plain English and watch as our AI generates beautiful Manim code automatically.",
      color: "from-blue-500 to-blue-600",
    },
    {
      icon: Code,
      title: "Clean Manim Code",
      description:
        "Get production-ready, well-commented Manim code that you can customize, learn from, and integrate into your projects.",
      color: "from-purple-500 to-purple-600",
    },
    {
      icon: Zap,
      title: "Lightning Fast",
      description:
        "Generate and render high-quality mathematical animations in seconds, not hours. Perfect for educators and content creators.",
      color: "from-yellow-500 to-orange-500",
    },
    {
      icon: Download,
      title: "Multiple Formats",
      description:
        "Export your animations in various formats including MP4, GIF, and PNG sequences for maximum compatibility.",
      color: "from-green-500 to-green-600",
    },
    {
      icon: Share,
      title: "Easy Sharing",
      description:
        "Share your mathematical animations with students, colleagues, or the world with built-in sharing and embedding options.",
      color: "from-pink-500 to-pink-600",
    },
    {
      icon: Clock,
      title: "Version History",
      description:
        "Keep track of all your animation iterations with automatic version control and the ability to revert to previous versions.",
      color: "from-indigo-500 to-indigo-600",
    },
  ]

  return (
    <section id="features" className="py-24 px-4">
      <div className="container mx-auto max-w-7xl">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Powerful Features for
            <span className="bg-gradient-to-r from-blue-400 to-blue-600 bg-clip-text text-transparent">
              {" "}
              Mathematical Visualization
            </span>
          </h2>
          <p className="text-xl text-slate-300 max-w-3xl mx-auto">
            Everything you need to create stunning mathematical animations, from simple concepts to complex
            visualizations.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              viewport={{ once: true }}
            >
              <Card className="bg-slate-900/50 border-blue-900/30 backdrop-blur-sm p-8 h-full hover:bg-slate-900/70 transition-all duration-300 group">
                <div
                  className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${feature.color} flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300`}
                >
                  <feature.icon className="w-8 h-8 text-white" />
                </div>

                <h3 className="text-2xl font-bold text-white mb-4 group-hover:text-blue-300 transition-colors">
                  {feature.title}
                </h3>

                <p className="text-slate-300 leading-relaxed">{feature.description}</p>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
