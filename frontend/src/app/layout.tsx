import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "LLM Compliance Test Suite",
  description: "Legal compliance testing for LLMs",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased font-body bg-background text-text">
        {/* Header */}
        <header className="w-full h-20 flex items-center px-8 bg-primary text-white justify-between">
          <div className="flex items-center space-x-4">
            <span className="text-3xl font-heading">⚖️</span>
            <span className="text-2xl font-heading font-bold">LLM Compliance Test Suite</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="inline-block w-3 h-3 rounded-full bg-success"></span>
            <span className="text-lg">Backend: Online</span>
          </div>
        </header>
        {/* Navigation Bar */}
        <nav>
          <Link href="/">Dashboard</Link> |{' '}
          <Link href="/use-cases">Use Cases</Link> |{' '}
          <Link href="/results">View Results</Link> |{' '}
          <Link href="/docs">Docs/Help</Link>
        </nav>
        <main className="px-8 py-8 min-h-[calc(100vh-8rem)] bg-background">
          {children}
        </main>
      </body>
    </html>
  );
}
