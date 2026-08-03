import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] });

export const metadata: Metadata = {
  metadataBase: new URL("https://proofedge-arm64.liu891855.chatgpt.site"),
  title: "ProofEdge — Evidence before confidence",
  description:
    "A local-first migration assurance agent with auditable evidence and reproducible native Arm64 benchmarks.",
  openGraph: {
    title: "ProofEdge",
    description: "Evidence before confidence. Private migration assurance on Arm64.",
    type: "website",
    images: [{ url: "/og.png", width: 1536, height: 1024, alt: "ProofEdge — Evidence before confidence" }],
  },
  twitter: {
    card: "summary_large_image",
    title: "ProofEdge",
    description: "Evidence before confidence. Private migration assurance on Arm64.",
    images: ["/og.png"],
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable}`}>{children}</body>
    </html>
  );
}
