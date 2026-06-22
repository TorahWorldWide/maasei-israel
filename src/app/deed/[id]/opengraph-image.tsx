import { ImageResponse } from "next/og";
import { getEntryById } from "@/lib/data";

export const alt = "מעשי ישראל";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default async function Image({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const entry = await getEntryById(id);
  const title = entry?.title ?? "מעשי ישראל";
  const category = entry?.category ?? "";

  return new ImageResponse(
    (
      <div
        style={{
          background: "#081026",
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "60px 80px",
          gap: 0,
        }}
      >
        {/* Star of David */}
        <svg
          width="72"
          height="72"
          viewBox="0 0 100 100"
          style={{ marginBottom: 28 }}
        >
          <polygon
            points="50,8 12,80 88,80"
            fill="none"
            stroke="#c9a84a"
            strokeWidth="5"
          />
          <polygon
            points="50,92 88,20 12,20"
            fill="none"
            stroke="#c9a84a"
            strokeWidth="5"
          />
        </svg>

        {/* Category chip */}
        {category && (
          <div
            style={{
              color: "#e6c66e",
              fontSize: 20,
              background: "rgba(201,168,74,0.15)",
              border: "1px solid rgba(201,168,74,0.3)",
              borderRadius: 24,
              padding: "4px 16px",
              marginBottom: 24,
            }}
          >
            {category}
          </div>
        )}

        {/* Entry title */}
        <div
          style={{
            color: "#e6c66e",
            fontSize: title.length > 50 ? 38 : title.length > 30 ? 46 : 54,
            fontWeight: 700,
            textAlign: "center",
            lineHeight: 1.35,
            maxWidth: 900,
            direction: "rtl",
            marginBottom: 32,
          }}
        >
          {title}
        </div>

        {/* Divider */}
        <div
          style={{
            width: 120,
            height: 2,
            background:
              "linear-gradient(to right, transparent, #c9a84a, transparent)",
            marginBottom: 24,
          }}
        />

        {/* Wordmark */}
        <div
          style={{
            color: "rgba(201,168,74,0.65)",
            fontSize: 26,
            letterSpacing: "0.04em",
            direction: "rtl",
          }}
        >
          מעשי ישראל
        </div>
      </div>
    ),
    { ...size }
  );
}
