// Counts approved deeds per century straight from Supabase, so the numbers the
// era chips show can be checked against the database.
// Run: node --env-file=.env.local scripts/verify-eras.mjs
import { createClient } from "@supabase/supabase-js";

const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
const key =
  process.env.SUPABASE_SERVICE_ROLE_KEY ?? process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
if (!url || !key) throw new Error("Missing Supabase env vars");

const { data, error } = await createClient(url, key)
  .from("entries")
  .select("id,year")
  .eq("status", "approved");
if (error) throw error;

const counts = new Map();
let missingYear = 0;
for (const { year } of data) {
  if (!year) {
    missingYear++;
    continue;
  }
  const from = Math.floor(year / 100) * 100;
  const key = `${from}-${from + 100}`;
  counts.set(key, (counts.get(key) ?? 0) + 1);
}

const rows = [...counts.entries()].sort((a, b) => Number(a[0].split("-")[0]) - Number(b[0].split("-")[0]));
for (const [era, n] of rows) console.log(era.padEnd(12), n);
console.log("-".repeat(20));
console.log("eras".padEnd(12), rows.length);
console.log("with year".padEnd(12), data.length - missingYear);
console.log("no year".padEnd(12), missingYear);
console.log("total".padEnd(12), data.length);
