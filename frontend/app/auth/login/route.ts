import { type NextRequest, NextResponse } from "next/server"
import jwt from "jsonwebtoken"
import bcrypt from "bcryptjs"

// This would typically connect to your MongoDB database
// For demo purposes, we'll simulate the database operations

export async function POST(request: NextRequest) {
  try {
    const { email, password } = await request.json()

    // Simulate database lookup
    // In real implementation, query MongoDB for user
    const user = {
      id: "1",
      email: email,
      name: "Demo User",
      password: await bcrypt.hash("password123", 10), // Simulated hashed password
    }

    // Verify password
    const isValidPassword = await bcrypt.compare(password, user.password)

    if (!isValidPassword) {
      return NextResponse.json({ error: "Invalid credentials" }, { status: 401 })
    }

    // Generate JWT token
    const token = jwt.sign({ userId: user.id, email: user.email }, process.env.JWT_SECRET || "your-secret-key", {
      expiresIn: "7d",
    })

    return NextResponse.json({
      token,
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
      },
    })
  } catch (error) {
    console.error("Login error:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}
