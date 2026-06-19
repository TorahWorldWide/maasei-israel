import { NextRequest, NextResponse } from "next/server";
import { insertSubmission } from "@/lib/data";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();

    if (
      !body.source_url ||
      typeof body.source_url !== "string" ||
      !body.source_url.trim()
    ) {
      return NextResponse.json(
        { ok: false, error: "מקור (source_url) הוא שדה חובה" },
        { status: 400 }
      );
    }

    if (!/^https?:\/\/.+/.test(body.source_url.trim())) {
      return NextResponse.json(
        { ok: false, error: "קישור מקור אינו תקין" },
        { status: 400 }
      );
    }

    const result = await insertSubmission({
      title: String(body.title ?? ""),
      description: String(body.description ?? ""),
      category: body.category ?? "חסד",
      year: typeof body.year === "number" ? body.year : null,
      media_type: body.media_type ?? "image",
      media_url: String(body.media_url ?? ""),
      source_url: body.source_url.trim(),
      source_label: String(body.source_label ?? ""),
      submitted_by: String(body.submitted_by ?? ""),
    });

    return NextResponse.json(result);
  } catch (err) {
    console.error("[/api/submit]", err);
    return NextResponse.json({ ok: false, error: "שגיאה פנימית" }, { status: 500 });
  }
}
