import type React from "react"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { AuthProvider } from "@/hooks/use-auth"
import { ChatProvider } from "@/hooks/use-chat"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "ManimAI - Mathematical Animation Generator",
  description: "Create stunning mathematical animations using AI-powered prompts and the Manim library",
  keywords: "manim, mathematics, animation, AI, education, visualization",
  authors: [{ name: "ManimAI Team" }],
  openGraph: {
    title: "ManimAI - Mathematical Animation Generator",
    description: "Create stunning mathematical animations using AI-powered prompts and the Manim library",
    type: "website",
    url: "https://manimai.com",
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>
        <AuthProvider>
          <ChatProvider>
            {children}
          </ChatProvider>
        </AuthProvider>
      </body>
    </html>
  )
}
