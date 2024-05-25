import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { UiProvider } from "@/providers/provider";
import NavigationBar from "@/components/navbar/navbar";
import AuthProvider from "@/providers/auth-provider";

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
    <html lang="en" className="dark">
      <body className={inter.className}>
        <AuthProvider>
          <UiProvider>
            <NavigationBar />
            <main className="min-h-[80vh]">{children}</main>
          </UiProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
