import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Navigationbar from "@/components/navbar/navbar";
import AuthProvider from "../providers/auth-provider";
import { UiProvider } from "@/providers/provider";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Career Coach",
  description: "An AI interview coach",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthProvider>
      <html lang="en" className="dark">
        <body className={inter.className}>
          <UiProvider>
            <Navigationbar />
            {children}
          </UiProvider>
        </body>
      </html>
    </AuthProvider>
  );
}
