"use client";
import { useEffect, useState } from "react";
import { supabase } from "../supabaseClient";

interface UseCase {
  id: string;
  regulation: string;
  scenario: string;
  question: string;
  expected_elements: string;
  updated_at: string;
}

export default function UseCasesPage() {
  const [useCases, setUseCases] = useState<UseCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState<UseCase | null>(null);
  const [form, setForm] = useState({
    regulation: "",
    scenario: "",
    question: "",
    expected_elements: "",
  });

  // Load use cases from Supabase
  useEffect(() => {
    async function fetchUseCases() {
      setLoading(true);
      setError(null);
      const { data, error } = await supabase
        .from("test_cases")
        .select("*")
        .order("updated_at", { ascending: false });
      if (error) setError(error.message);
      else setUseCases(data || []);
      setLoading(false);
    }
    fetchUseCases();
  }, []);

  // Handle form input changes
  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  // Open modal for add or edit
  function openModal(useCase?: UseCase) {
    if (useCase) {
      setEditing(useCase);
      setForm({
        regulation: useCase.regulation,
        scenario: useCase.scenario,
        question: useCase.question,
        expected_elements: useCase.expected_elements,
      });
    } else {
      setEditing(null);
      setForm({ regulation: "", scenario: "", question: "", expected_elements: "" });
    }
    setShowModal(true);
  }

  // Close modal
  function closeModal() {
    setShowModal(false);
    setEditing(null);
    setForm({ regulation: "", scenario: "", question: "", expected_elements: "" });
  }

  // Add or update use case
  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    if (editing) {
      // Update
      const { error } = await supabase
        .from("test_cases")
        .update({ ...form, updated_at: new Date().toISOString() })
        .eq("id", editing.id);
      if (error) setError(error.message);
    } else {
      // Insert
      const { error } = await supabase
        .from("test_cases")
        .insert([{ ...form, updated_at: new Date().toISOString() }]);
      if (error) setError(error.message);
    }
    // Refresh list
    const { data, error: fetchError } = await supabase
      .from("test_cases")
      .select("*")
      .order("updated_at", { ascending: false });
    if (fetchError) setError(fetchError.message);
    else setUseCases(data || []);
    setLoading(false);
    closeModal();
  }

  // Delete use case
  async function handleDelete(id: string) {
    setLoading(true);
    setError(null);
    const { error } = await supabase.from("test_cases").delete().eq("id", id);
    if (error) setError(error.message);
    setUseCases(useCases.filter((u) => u.id !== id));
    setLoading(false);
  }

  return (
    <div>
      <h1 className="text-2xl font-heading font-bold text-primary mb-4">Use Cases</h1>
      <p className="text-lg text-secondary mb-8">Manage, add, and edit compliance test use cases here.</p>
      <button
        className="mb-4 px-6 py-2 rounded bg-accent text-white font-medium hover:bg-blue-800 flex items-center gap-2"
        onClick={() => openModal()}
        aria-label="Add New Use Case"
      >
        {/* Plus SVG icon */}
        <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" aria-hidden="true"><path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4"/></svg>
        Add New Use Case
      </button>
      {loading && <div className="text-secondary">Loading...</div>}
      {error && <div className="text-error">Error: {error}</div>}
      <div className="bg-white rounded-xl shadow border-2 border-neutral w-full max-w-6xl mx-auto">
        <div className="overflow-x-auto">
          <table className="min-w-full text-left">
            <thead>
              <tr className="bg-neutral">
                <th className="px-4 py-2 text-accent font-semibold">Regulation</th>
                <th className="px-4 py-2 text-accent font-semibold">Scenario</th>
                <th className="px-4 py-2 text-accent font-semibold">Question</th>
                <th className="px-4 py-2 text-accent font-semibold">Expected Elements</th>
                <th className="px-4 py-2 text-accent font-semibold">Updated</th>
                <th className="px-4 py-2 text-accent font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody>
              {useCases.map((u) => (
                <tr key={u.id} className="even:bg-neutral">
                  <td className="px-4 py-2 align-top max-w-xs break-words">{u.regulation}</td>
                  <td className="px-4 py-2 align-top max-w-xs break-words">{u.scenario}</td>
                  <td className="px-4 py-2 align-top max-w-xs break-words">{u.question}</td>
                  <td className="px-4 py-2 align-top max-w-xs break-words">{u.expected_elements}</td>
                  <td className="px-4 py-2 align-top whitespace-nowrap">{u.updated_at?.slice(0, 10)}</td>
                  <td className="px-4 py-2 align-top">
                    <button
                      className="mr-2 text-accent hover:underline"
                      onClick={() => openModal(u)}
                    >
                      ✏️
                    </button>
                    <button
                      className="text-error hover:underline"
                      onClick={() => handleDelete(u.id)}
                    >
                      🗑️
                    </button>
                  </td>
                </tr>
              ))}
              {useCases.length === 0 && !loading && (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-secondary">
                    No use cases found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
      {/* Modal for Add/Edit */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg p-8 w-full max-w-xl">
            <h2 className="text-xl font-heading font-bold mb-4">
              {editing ? "Edit Use Case" : "Add Use Case"}
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block font-medium mb-1">Regulation</label>
                <input
                  type="text"
                  name="regulation"
                  value={form.regulation}
                  onChange={handleChange}
                  className="w-full border rounded px-3 py-2"
                  required
                />
              </div>
              <div>
                <label className="block font-medium mb-1">Scenario</label>
                <textarea
                  name="scenario"
                  value={form.scenario}
                  onChange={handleChange}
                  className="w-full border rounded px-3 py-2"
                  rows={2}
                  required
                />
              </div>
              <div>
                <label className="block font-medium mb-1">Question</label>
                <textarea
                  name="question"
                  value={form.question}
                  onChange={handleChange}
                  className="w-full border rounded px-3 py-2"
                  rows={2}
                  required
                />
              </div>
              <div>
                <label className="block font-medium mb-1">Expected Elements</label>
                <textarea
                  name="expected_elements"
                  value={form.expected_elements}
                  onChange={handleChange}
                  className="w-full border rounded px-3 py-2"
                  rows={2}
                  required
                />
              </div>
              <div className="flex justify-end gap-2 mt-4">
                <button
                  type="button"
                  className="px-4 py-2 rounded bg-neutral text-text hover:bg-gray-300"
                  onClick={closeModal}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded bg-success text-white font-medium hover:bg-green-700"
                  disabled={loading}
                >
                  {editing ? "Update" : "Add"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
} 