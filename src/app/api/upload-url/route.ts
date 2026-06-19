import { NextRequest, NextResponse } from "next/server";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const serviceKey =
  process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_SECRET_KEY;

const BUCKET = "media";
const MAX_BYTES = 52428800; // 50 MB
const ALLOWED = [
  "video/mp4",
  "video/quicktime",
  "video/webm",
  "video/x-matroska",
  "video/3gpp",
  "image/jpeg",
  "image/png",
  "image/webp",
  "image/gif",
];

const EXT: Record<string, string> = {
  "video/mp4": "mp4",
  "video/quicktime": "mov",
  "video/webm": "webm",
  "video/x-matroska": "mkv",
  "video/3gpp": "3gp",
  "image/jpeg": "jpg",
  "image/png": "png",
  "image/webp": "webp",
  "image/gif": "gif",
};

let bucketReady = false;

async function getServiceClient() {
  const { createClient } = await import("@supabase/supabase-js");
  return createClient(supabaseUrl!, serviceKey!);
}

async function ensureBucket(client: Awaited<ReturnType<typeof getServiceClient>>) {
  if (bucketReady) return;
  const { error } = await client.storage.createBucket(BUCKET, {
    public: true,
    fileSizeLimit: MAX_BYTES,
    allowedMimeTypes: ALLOWED,
  });
  // "already exists" is fine — treat as success.
  if (error && !/exist/i.test(error.message)) {
    throw new Error(error.message);
  }
  bucketReady = true;
}

export async function POST(req: NextRequest) {
  if (!supabaseUrl || !serviceKey) {
    return NextResponse.json(
      { ok: false, error: "אחסון אינו מוגדר" },
      { status: 503 }
    );
  }

  try {
    const { contentType, size } = await req.json();

    if (!contentType || !ALLOWED.includes(contentType)) {
      return NextResponse.json(
        { ok: false, error: "סוג קובץ לא נתמך. מותר וידאו או תמונה בלבד." },
        { status: 400 }
      );
    }
    if (typeof size === "number" && size > MAX_BYTES) {
      return NextResponse.json(
        { ok: false, error: "הקובץ גדול מדי. מקסימום 50MB." },
        { status: 400 }
      );
    }

    const client = await getServiceClient();
    await ensureBucket(client);

    const ext = EXT[contentType] ?? "bin";
    const path = `uploads/${Date.now()}-${Math.random()
      .toString(36)
      .slice(2, 10)}.${ext}`;

    const { data, error } = await client.storage
      .from(BUCKET)
      .createSignedUploadUrl(path);

    if (error || !data) {
      return NextResponse.json(
        { ok: false, error: error?.message ?? "נכשלה יצירת קישור העלאה" },
        { status: 500 }
      );
    }

    // data.signedUrl is the canonical upload target (path under the project URL,
    // token embedded). Build an absolute URL the browser can PUT to directly.
    const signed = data.signedUrl;
    const uploadUrl = /^https?:\/\//.test(signed)
      ? signed
      : `${supabaseUrl}${signed.startsWith("/") ? "" : "/"}${signed}`;

    const publicUrl = `${supabaseUrl}/storage/v1/object/public/${BUCKET}/${path}`;

    return NextResponse.json({
      ok: true,
      bucket: BUCKET,
      path: data.path,
      token: data.token,
      uploadUrl,
      publicUrl,
    });
  } catch (err) {
    console.error("[/api/upload-url]", err);
    return NextResponse.json(
      { ok: false, error: "שגיאה פנימית" },
      { status: 500 }
    );
  }
}
