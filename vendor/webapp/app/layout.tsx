import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Sloth Experimental",
  description: "Experimental app for Sloth to design admin UI",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
        {children}
    </html>
  );
}
