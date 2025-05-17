import SidePanel from "@/app/components/side-panel/side-panel";
import React from "react";
import styles from './app.module.css';

export default function SlothLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <body className={styles.sBody}>
        <SidePanel />
        {children}
    </body>
  );
}