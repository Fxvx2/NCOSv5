"use client";
import { useState, useEffect } from "react";
import { supabase } from "../supabaseClient";
import { useRouter } from "next/navigation";

interface UseCase {
  id: string;
  regulation: string;
  scenario: string;
  question: string;
}

export default function RunTestPage() {
  const [useCases, setUseCases] = useState<UseCase[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  useEffect(() => {
    supabase
      .from("test_cases")
      .select("id, regulation, scenario, question")
      .order("updated_at", { ascending: false })
      .then(({ data }) => setUseCases(data || []));
  }, []);

  async function handleRunTest(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedId) return;
    setLoading(true);
    // Fetch the selected use case
    const { data } = await supabase.from("test_cases").select("*").eq("id", selectedId).single();
    if (!data) {
      setLoading(false);
      return;
    }
    // Call backend to run inference
    await fetch("/api/run-inference", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ useCase: data }),
    });
    setLoading(false);
    router.push("/results");
  }

  return (
    <div style={{ maxWidth: 400, margin: "40px auto", padding: 24, background: "white", borderRadius: 8, boxShadow: "0 2px 8px rgba(0,0,0,0.05)" }}>
      <h1 style={{ fontWeight: "bold", fontSize: 24, marginBottom: 24 }}>Run New Test</h1>
      <form onSubmit={handleRunTest}>
        <label>Select a use case:</label>
        <select value={selectedId} onChange={e => setSelectedId(e.target.value)} style={{ width: "100%", marginBottom: 16 }}>
          <option value="">-- Select --</option>
          {useCases.map((u) => (
            <option key={u.id} value={u.id}>{u.regulation} - {u.scenario}</option>
          ))}
        </select>
        <div style={{ display: "flex", justifyContent: "flex-end", gap: 8 }}>
          <button type="submit" disabled={!selectedId || loading}>{loading ? "Running..." : "Run"}</button>
        </div>
      </form>
    </div>
  );
} 