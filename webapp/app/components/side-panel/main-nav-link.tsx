'use client'; // indicates if it's client side component

import {usePathname} from "next/navigation";
import Link from "next/link";
import styles from "./side-panel.module.css";
import {JSX} from "react";

interface MainNavLinkProps {
	href: string,
	startsWith?: boolean,
	children: string | JSX.Element | JSX.Element[],
}

export default function MainNavLink({ href, children, startsWith = false }: MainNavLinkProps) {
	const path = usePathname();

	let className = undefined;
	if (startsWith) {
		className = path.startsWith(href) ? styles.active : undefined;
	} else {
		className = path === href ? styles.active : undefined;
	}

	return (
		<Link href={href} className={className}>{children}</Link>
	)
}