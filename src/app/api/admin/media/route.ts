import { NextRequest, NextResponse } from "next/server";
import { listEntriesWithMedia, reorderEntryMedia, NOT_A_REORDER } from "@/lib/data";

function checkAuth(req: NextRequest): boolean {
  const adminPassword = process.env.ADMIN_PASSWORD;
  if (!adminPassword) return false;
  return req.headers.get("x-admin-password") === adminPassword;
}

function unauthorized() {
  return NextResponse.json(
    { ok: false, code: "unauthorized", error: "Unauthorized" },
    { status: 401 }
  );
}

export async function GET(req: NextRequest) {
  if (!checkAuth(req)) return unauthorized();
  try {
    return NextResponse.json({ ok: true, entries: await listEntriesWithMedia() });
  } catch (err) {
    console.error("[/api/admin/media GET]", err);
    return NextResponse.json(
      { ok: false, code: "internal", error: "שגיאה פנימית" },
      { status: 500 }
    );
  }
}

export async function POST(req: NextRequest) {
  if (!checkAuth(req)) return unauthorized();
  try {
    const { id, media_urls } = await req.json();
    if (!id || !Array.isArray(media_urls) || media_urls.some((u) => typeof u !== "string")) {
      return NextResponse.json(
        { ok: false, code: "bad_request", error: "Missing id or media_urls" },
        { status: 400 }
      );
    }
    const written = await reorderEntryMedia(String(id), media_urls as string[]);
    return NextResponse.json({ ok: true, media_urls: written });
  } catch (err) {
    if (err instanceof Error && err.message === NOT_A_REORDER) {
      return NextResponse.json(
        { ok: false, code: "not_a_reorder", error: err.message },
        { status: 400 }
      );
    }
    console.error("[/api/admin/media POST]", err);
    return NextResponse.json(
      { ok: false, code: "internal", error: "שגיאה פנימית" },
      { status: 500 }
    );
  }
}
