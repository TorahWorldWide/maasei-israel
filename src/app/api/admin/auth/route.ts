import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  const adminPassword = process.env.ADMIN_PASSWORD;

  if (!adminPassword) {
    return NextResponse.json({
      ok: false,
      reason: "unconfigured",
      message: "ADMIN_PASSWORD not set — admin disabled.",
    });
  }

  try {
    const { password } = await req.json();
    if (password !== adminPassword) {
      return NextResponse.json(
        { ok: false, reason: "invalid" },
        { status: 401 }
      );
    }
    return NextResponse.json({ ok: true });
  } catch {
    return NextResponse.json({ ok: false, reason: "error" }, { status: 400 });
  }
}
