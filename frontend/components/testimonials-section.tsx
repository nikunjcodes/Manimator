"use client"

import { motion } from "framer-motion"
import { Card } from "@/components/ui/card"
import { Star, Quote } from "lucide-react"

export function TestimonialsSection() {
  const testimonials = [
    {
      name: "Dr. Sarah Chen",
      role: "Mathematics Professor",
      institution: "MIT",
      content:
        "ManimAI has revolutionized how I create educational content. What used to take hours now takes minutes, and the quality is exceptional.",
      rating: 5,
      avatar: "/placeholder.svg?height=60&width=60",
    },
    {
      name: "Michael Rodriguez",
      role: "High School Teacher",
      institution: "Lincoln High School",
      content:
        "My students are more engaged than ever. The animations help them visualize complex concepts that were previously abstract.",
      rating: 5,
      avatar: "/placeholder.svg?height=60&width=60",
    },
    {
      name: "Dr. Emily Watson",
      role: "Research Scientist",
      institution: "Stanford University",
      content:
        "The AI-generated code is clean and educational. It's not just a tool for creating animations, but for learning Manim itself.",
      rating: 5,
      avatar: "/placeholder.svg?height=60&width=60",
    },
    {
      name: "James Park",
      role: "Content Creator",
      institution: "YouTube Educator",
      content:
        "As someone who creates math content online, ManimAI has been a game-changer. The quality and speed are unmatched.",
      rating: 5,
      avatar: "/placeholder.svg?height=60&width=60",
    },
    {
      name: "Dr. Lisa Thompson",
      role: "Curriculum Designer",
      institution: "Khan Academy",
      content:
        "We've integrated ManimAI into our content creation workflow. It's incredibly intuitive and produces professional results.",
      rating: 5,
      avatar: "/placeholder.svg?height=60&width=60",
    },
    {
      name: "Alex Kumar",
      role: "Graduate Student",
      institution: "UC Berkeley",
      content:
        "Perfect for my thesis presentations. The animations help explain my research in a way that's accessible to everyone.",
      rating: 5,
      avatar: "/placeholder.svg?height=60&width=60",
    },
  ]

  return (
    <section className="py-24 px-4 bg-slate-900/30">
      <div className="container mx-auto max-w-7xl">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            What Our
            <span className="bg-gradient-to-r from-blue-400 to-blue-600 bg-clip-text text-transparent"> Users Say</span>
          </h2>
          <p className="text-xl text-slate-300 max-w-3xl mx-auto">
            Don't just take our word for it. Here's what educators and creators are saying about ManimAI.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {testimonials.map((testimonial, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              viewport={{ once: true }}
            >
              <Card className="bg-slate-900/50 border-blue-900/30 backdrop-blur-sm p-8 h-full hover:bg-slate-900/70 transition-all duration-300 relative">
                <Quote className="absolute top-6 right-6 w-8 h-8 text-blue-400/30" />

                <div className="flex items-center mb-6">
                  <img
                    src={testimonial.avatar || "/placeholder.svg"}
                    alt={testimonial.name}
                    className="w-12 h-12 rounded-full mr-4"
                  />
                  <div>
                    <h4 className="text-white font-semibold">{testimonial.name}</h4>
                    <p className="text-blue-300 text-sm">{testimonial.role}</p>
                    <p className="text-slate-400 text-xs">{testimonial.institution}</p>
                  </div>
                </div>

                <div className="flex items-center mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} className="w-4 h-4 text-yellow-400 fill-current" />
                  ))}
                </div>

                <p className="text-slate-300 leading-relaxed italic">"{testimonial.content}"</p>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
