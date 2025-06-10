import { type NextRequest, NextResponse } from "next/server"
import jwt from "jsonwebtoken"

export async function GET(request: NextRequest) {
  try {
    const authHeader = request.headers.get("authorization")
    const token = authHeader?.replace("Bearer ", "")

    if (!token) {
      return NextResponse.json({ error: "No token provided" }, { status: 401 })
    }

    // Verify JWT token
    const decoded = jwt.verify(token, process.env.JWT_SECRET || "your-secret-key") as any

    // Simulate database lookup for user
    const user = {
      id: decoded.userId,
      email: decoded.email,
      name: "Demo User",
    }

    return NextResponse.json(user)
  } catch (error) {
    console.error("Token validation error:", error)
    return NextResponse.json({ error: "Invalid token" }, { status: 401 })
  }
}
