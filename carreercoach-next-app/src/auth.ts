import NextAuth from "next-auth/next";
import { nextauthOptions } from "./lib/nextauth-options";

export const { handlers, auth, signIn, signOut } = NextAuth(nextauthOptions);
