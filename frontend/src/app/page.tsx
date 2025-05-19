import { useState, useEffect } from "react";
import { supabase } from "./supabaseClient";
import { useRouter } from "next/navigation";

// Define the use case type
interface UseCase {
  id: string;
  regulation: string;
  scenario: string;
  question: string;
}

export default function Home() {
  const [showModal, setShowModal] = useState(false);
  const [useCases, setUseCases] = useState<UseCase[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  useEffect(() => {
    if (showModal) {
      supabase
        .from("test_cases")
        .select("id, regulation, scenario, question")
        .order("updated_at", { ascending: false })
        .then(({ data }) => setUseCases(data || []));
    }
  }, [showModal]);

  async function handleRunTest() {
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
    setShowModal(false);
    router.push("/results");
  }

  return (
    <div>
      {/* Quick Actions */}
      <div>
        <a href="/run-test" style={{ marginRight: '1em' }}>Run New Test</a>
        <a href="/use-cases" style={{ marginRight: '1em' }}>Add Use Case</a>
        <a href="/results">View Results</a>
      </div>
      {/* Modal for Run New Test */}
      {showModal && (
        <div style={{ position: "fixed", top: 0, left: 0, width: "100vw", height: "100vh", background: "rgba(0,0,0,0.3)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000 }}>
          <div style={{ background: "white", padding: 24, borderRadius: 8, minWidth: 320 }}>
            <h2 style={{ fontWeight: "bold", fontSize: 20, marginBottom: 16 }}>Run New Test</h2>
            <label>Select a use case:</label>
            <select value={selectedId} onChange={e => setSelectedId(e.target.value)} style={{ width: "100%", marginBottom: 16 }}>
              <option value="">-- Select --</option>
              {useCases.map((u) => (
                <option key={u.id} value={u.id}>{u.regulation} - {u.scenario}</option>
              ))}
            </select>
            <div style={{ display: "flex", justifyContent: "flex-end", gap: 8 }}>
              <button onClick={() => setShowModal(false)} disabled={loading}>Cancel</button>
              <button onClick={handleRunTest} disabled={!selectedId || loading}>{loading ? "Running..." : "Run"}</button>
            </div>
          </div>
        </div>
      )}
      {/* Use Case Table Placeholder */}
      <div className="bg-white rounded-xl shadow border-2 border-neutral w-full max-w-5xl mx-auto">
        <div className="px-6 py-4 border-b border-neutral flex items-center justify-between">
          <h2 className="text-xl font-heading font-bold text-primary">Use Cases</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full text-left">
            <thead>
              <tr className="bg-neutral">
                <th className="px-6 py-3 text-accent font-semibold">Title</th>
                <th className="px-6 py-3 text-accent font-semibold">Description</th>
                <th className="px-6 py-3 text-accent font-semibold">Updated</th>
                <th className="px-6 py-3 text-accent font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr className="bg-neutral">
                <td className="px-6 py-4 text-text">GDPR Right to Erasure</td>
                <td className="px-6 py-4 text-text">Test if model forgets user data</td>
                <td className="px-6 py-4 text-text">2025-05-16</td>
                <td className="px-6 py-4 text-accent text-xl">✏️ 🗑️ ▶️</td>
              </tr>
              <tr className="bg-white">
                <td className="px-6 py-4 text-text">Bias Detection</td>
                <td className="px-6 py-4 text-text">Check for demographic bias</td>
                <td className="px-6 py-4 text-text">2025-05-15</td>
                <td className="px-6 py-4 text-accent text-xl">✏️ 🗑️ ▶️</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
