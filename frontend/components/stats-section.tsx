"use client"

import { motion } from "framer-motion"
import { Users, Play, Clock, Star } from "lucide-react"

export function StatsSection() {
  const stats = [
    {
      icon: Users,
      number: "10,000+",
      label: "Active Users",
      description: "Educators and students worldwide",
    },
    {
      icon: Play,
      number: "50,000+",
      label: "Animations Created",
      description: "Mathematical visualizations generated",
    },
    {
      icon: Clock,
      number: "1M+",
      label: "Hours Saved",
      description: "Time saved on animation creation",
    },
    {
      icon: Star,
      number: "4.9/5",
      label: "User Rating",
      description: "Based on 2,000+ reviews",
    },
  ]

  return (
    <section className="py-24 px-4">
      <div className="container mx-auto max-w-7xl">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Trusted by
            <span className="bg-gradient-to-r from-blue-400 to-blue-600 bg-clip-text text-transparent"> Thousands</span>
          </h2>
          <p className="text-xl text-slate-300 max-w-3xl mx-auto">
            Join a growing community of educators, students, and content creators who are revolutionizing mathematical
            education.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {stats.map((stat, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              viewport={{ once: true }}
              className="text-center group"
            >
              <div className="w-20 h-20 bg-gradient-to-br from-blue-500/20 to-blue-600/20 rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform duration-300">
                <stat.icon className="w-10 h-10 text-blue-400" />
              </div>

              <motion.div
                initial={{ scale: 0.5 }}
                whileInView={{ scale: 1 }}
                transition={{ duration: 0.8, delay: index * 0.1 + 0.3 }}
                viewport={{ once: true }}
                className="text-4xl md:text-5xl font-bold text-white mb-2"
              >
                {stat.number}
              </motion.div>

              <h3 className="text-xl font-semibold text-blue-300 mb-2">{stat.label}</h3>

              <p className="text-slate-400 text-sm">{stat.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
