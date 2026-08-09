import { NextRequest, NextResponse } from "next/server";
import { rejectSubmission } from "@/lib/data";

function checkAuth(req: NextRequest): boolean {
  const adminPassword = process.env.ADMIN_PASSWORD;
  if (!adminPassword) return false;
  return req.headers.get("x-admin-password") === adminPassword;
}

export async function POST(req: NextRequest) {
  if (!checkAuth(req)) {
    return NextResponse.json(
      { ok: false, code: "unauthorized", error: "Unauthorized" },
      { status: 401 }
    );
  }
  try {
    const { id } = await req.json();
    if (!id)
      return NextResponse.json(
        { ok: false, code: "missing_id", error: "Missing id" },
        { status: 400 }
      );
    await rejectSubmission(String(id));
    return NextResponse.json({ ok: true });
  } catch (err) {
    console.error("[/api/admin/reject]", err);
    return NextResponse.json(
      { ok: false, code: "internal", error: "שגיאה פנימית" },
      { status: 500 }
    );
  }
}
