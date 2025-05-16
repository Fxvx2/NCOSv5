import Image from "next/image";

export default function Home() {
  return (
    <div>
      {/* Quick Actions */}
      <div className="flex flex-col sm:flex-row gap-4 mb-8">
        <button className="px-6 py-3 rounded-lg bg-success text-white font-medium text-lg hover:bg-green-700 transition">Run New Test</button>
        <button className="px-6 py-3 rounded-lg bg-accent text-white font-medium text-lg hover:bg-blue-800 transition">Add Use Case</button>
        <button className="px-6 py-3 rounded-lg bg-primary text-white font-medium text-lg hover:bg-indigo-900 transition">View Results</button>
      </div>
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
