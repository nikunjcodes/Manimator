"use client"

import { useState } from "react"
import { motion, useScroll, useTransform } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Sparkles, Code2, Zap, Brain, Rocket } from "lucide-react"
import { HeroSection } from "@/components/hero-section"
import { FeaturesSection } from "@/components/features-section"
import { StatsSection } from "@/components/stats-section"
import { CTASection } from "@/components/cta-section"
import { Footer } from "@/components/footer"
import { AuthModal } from "@/components/auth-modal"
import { useAuth } from "@/hooks/use-auth"

export default function HomePage() {
  const [showAuth, setShowAuth] = useState(false)
  const { user, isAuthenticated } = useAuth()
  const { scrollYProgress } = useScroll()
  const opacity = useTransform(scrollYProgress, [0, 0.2], [1, 0])

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-blue-950 relative overflow-hidden">
      {/* Enhanced Background Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        {/* Primary gradient orbs with improved colors and animations */}
        <motion.div
          className="absolute -top-40 -right-40 w-[500px] h-[500px] bg-gradient-to-br from-blue-600/20 via-cyan-500/15 to-purple-500/10 rounded-full blur-[100px]"
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.4, 0.6, 0.4],
            rotate: [0, 180, 360],
          }}
          transition={{
            duration: 25,
            repeat: Number.POSITIVE_INFINITY,
            ease: "easeInOut",
          }}
        />
        <motion.div
          className="absolute -bottom-40 -left-40 w-[500px] h-[500px] bg-gradient-to-tr from-indigo-600/20 via-purple-500/15 to-pink-500/10 rounded-full blur-[100px]"
          animate={{
            scale: [1.2, 1, 1.2],
            opacity: [0.3, 0.5, 0.3],
            rotate: [360, 180, 0],
          }}
          transition={{
            duration: 30,
            repeat: Number.POSITIVE_INFINITY,
            ease: "easeInOut",
            delay: 5,
          }}
        />
        <motion.div
          className="absolute top-1/3 left-1/3 w-[400px] h-[400px] bg-gradient-to-r from-cyan-500/15 via-blue-500/10 to-indigo-500/5 rounded-full blur-[100px]"
          animate={{
            x: [-100, 150, -100],
            y: [-50, 100, -50],
            scale: [1, 1.1, 1],
          }}
          transition={{
            duration: 35,
            repeat: Number.POSITIVE_INFINITY,
            ease: "easeInOut",
          }}
        />

        {/* Enhanced floating math symbols with improved styling */}
        {["∫", "∑", "π", "∞", "∂", "√", "α", "β", "γ", "θ", "λ", "μ"].map((symbol, index) => (
          <motion.div
            key={symbol}
            className="absolute text-blue-400/20 font-mono select-none"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              fontSize: `${Math.random() * 2.5 + 2}rem`,
              filter: "blur(0.5px)",
            }}
            initial={{
              opacity: 0,
              y: 100,
            }}
            animate={{
              opacity: [0, 0.4, 0],
              y: -150,
              rotate: [0, 360],
              scale: [0.8, 1.2, 0.8],
            }}
            transition={{
              duration: Math.random() * 25 + 20,
              repeat: Number.POSITIVE_INFINITY,
              delay: index * 2.5,
              ease: "linear",
            }}
          >
            {symbol}
          </motion.div>
        ))}
      </div>

      {/* Enhanced Navigation with improved styling */}
      <motion.header
        className="fixed top-0 w-full z-50 backdrop-blur-xl bg-slate-950/50 border-b border-blue-900/20"
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
      >
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <motion.div
              className="flex items-center space-x-4"
              whileHover={{ scale: 1.02 }}
              transition={{ type: "spring", stiffness: 400, damping: 10 }}
            >
              <div className="relative">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 via-blue-600 to-cyan-500 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/25 animate-glow">
                  <Sparkles className="w-7 h-7 text-white" />
                </div>
                <div className="absolute -inset-1 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-xl blur opacity-30 animate-pulse" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent tracking-tight">
                  ManimAI
                </h1>
                <p className="text-xs text-slate-400 font-medium tracking-wide">AI-Powered Math Animations</p>
              </div>
            </motion.div>

            <nav className="hidden md:flex items-center space-x-8">
              {[
                { name: "Features", icon: Zap },
                { name: "How It Works", icon: Brain },
                { name: "Examples", icon: Code2 },
                { name: "Pricing", icon: Rocket },
              ].map((item, index) => (
                <motion.a
                  key={item.name}
                  href={`#${item.name.toLowerCase().replace(" ", "-")}`}
                  className="text-slate-300 hover:text-blue-400 transition-all duration-300 font-medium relative group flex items-center space-x-2"
                  whileHover={{ y: -2 }}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 * index + 0.5 }}
                >
                  <item.icon className="w-4 h-4" />
                  <span>{item.name}</span>
                  <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-to-r from-blue-400 to-cyan-400 group-hover:w-full transition-all duration-300" />
                </motion.a>
              ))}
            </nav>

            <div className="flex items-center space-x-4">
              {isAuthenticated ? (
                <motion.div
                  className="flex items-center space-x-3"
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.3 }}
                >
                  <Badge variant="outline" className="border-blue-500/30 text-blue-400 bg-blue-500/10 backdrop-blur-sm">
                    {user?.email}
                  </Badge>
                  <Button
                    variant="outline"
                    size="sm"
                    className="border-blue-500/30 text-blue-400 hover:bg-blue-500/10 backdrop-blur-sm transition-all duration-300"
                  >
                    Dashboard
                  </Button>
                </motion.div>
              ) : (
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.6 }}
                >
                  <Button
                    onClick={() => setShowAuth(true)}
                    className="relative px-6 py-2.5 rounded-xl font-semibold bg-gradient-to-r from-blue-500 to-cyan-500 text-white hover:from-blue-600 hover:to-cyan-600 transition-all duration-300 shadow-lg shadow-blue-500/25"
                  >
                    <span className="relative z-10">Get Started</span>
                    <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-xl blur opacity-50 animate-pulse" />
                  </Button>
                </motion.div>
              )}
            </div>
          </div>
        </div>
      </motion.header>

      {/* Main Content */}
      <div className="relative z-10 pt-20">
        <HeroSection onGetStarted={() => setShowAuth(true)} />
        <FeaturesSection />
        <StatsSection />
        <CTASection onGetStarted={() => setShowAuth(true)} />
        <Footer />
      </div>

      {/* Enhanced Scroll Indicator */}
      <motion.div className="fixed bottom-8 left-1/2 transform -translate-x-1/2 z-40" style={{ opacity }}>
        <motion.div
          animate={{ y: [0, 12, 0] }}
          transition={{ duration: 2.5, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut" }}
          className="flex flex-col items-center text-blue-400/80 group cursor-pointer"
        >
          <span className="text-sm mb-3 font-medium tracking-wide group-hover:text-blue-300 transition-colors">
            Scroll to explore
          </span>
          <div className="w-6 h-10 border-2 border-blue-400/40 rounded-full flex justify-center group-hover:border-blue-300/60 transition-colors">
            <motion.div
              animate={{ y: [0, 12, 0] }}
              transition={{ duration: 2, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut" }}
              className="w-1 h-3 bg-gradient-to-b from-blue-400 to-cyan-400 rounded-full mt-2"
            />
          </div>
        </motion.div>
      </motion.div>

      <AuthModal open={showAuth} onOpenChange={setShowAuth} />
    </div>
  )
}
