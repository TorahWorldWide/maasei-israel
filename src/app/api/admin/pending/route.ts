import { NextRequest, NextResponse } from "next/server";
import { listPending } from "@/lib/data";

function checkAuth(req: NextRequest): boolean {
  const adminPassword = process.env.ADMIN_PASSWORD;
  if (!adminPassword) return false;
  const provided = req.headers.get("x-admin-password");
  return provided === adminPassword;
}

export async function GET(req: NextRequest) {
  if (!checkAuth(req)) {
    return NextResponse.json(
      { ok: false, code: "unauthorized", error: "Unauthorized" },
      { status: 401 }
    );
  }
  try {
    const result = await listPending();
    return NextResponse.json(result);
  } catch (err) {
    console.error("[/api/admin/pending]", err);
    return NextResponse.json(
      { ok: false, code: "internal", error: "שגיאה פנימית" },
      { status: 500 }
    );
  }
}
