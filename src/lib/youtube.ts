// Shared YouTube helpers used by the theater stage and the deed page.

// Extract the 11-char video id from any common YouTube url shape.
export function ytId(url: string | null | undefined): string | null {
  const m = (url || "").match(
    /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})/
  );
  return m ? m[1] : null;
}

// YouTube IFrame Player API error codes that mean "this video will NOT play
// inline on our site" — removed/private (100), or embedding disabled by the
// owner (101/150, the "watch on YouTube" case Tomer hit). 2 and 5 are player
// errors. Any of these → we show a graceful fallback instead of a dead frame.
export const YT_UNPLAYABLE_ERRORS = new Set([2, 5, 100, 101, 150]);

// Load the YouTube IFrame API once, shared across the whole app.
let ytApiPromise: Promise<void> | null = null;
export function loadYouTubeApi(): Promise<void> {
  if (typeof window === "undefined") return Promise.resolve();
  if (ytApiPromise) return ytApiPromise;
  ytApiPromise = new Promise<void>((resolve) => {
    interface YTWindow {
      YT?: { Player: unknown };
      onYouTubeIframeAPIReady?: () => void;
    }
    const w = window as unknown as YTWindow;
    if (w.YT && w.YT.Player) {
      resolve();
      return;
    }
    const prev = w.onYouTubeIframeAPIReady;
    w.onYouTubeIframeAPIReady = () => {
      if (prev) prev();
      resolve();
    };
    if (!document.getElementById("yt-iframe-api")) {
      const tag = document.createElement("script");
      tag.id = "yt-iframe-api";
      tag.src = "https://www.youtube.com/iframe_api";
      document.head.appendChild(tag);
    }
  });
  return ytApiPromise;
}
