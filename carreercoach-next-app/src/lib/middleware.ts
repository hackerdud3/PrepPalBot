import NextAuth from "next-auth/next";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import {
  DEFAULT_LOGIN_REDIRECT,
  apiAuthPrefix,
  authRoutes,
  publicRoutes,
} from "./protected-routes";
import { nextauthOptions } from "./nextauth-options";

const { auth } = NextAuth(nextauthOptions);

// This function can be marked `async` if using `await` inside
export function middleware(request: NextRequest) {
  const { nextUrl } = request;
  const isLoggedIn = auth?.session?.user;
  const isPublicRoutes = publicRoutes.includes(nextUrl.pathname);
  const isAuthRoute = authRoutes.includes(nextUrl.pathname);
  const isApiAuthRoute = nextUrl.pathname.startsWith(apiAuthPrefix);
  if (isApiAuthRoute) {
    return null;
  }
  if (isAuthRoute && isLoggedIn) {
    return NextResponse.redirect(new URL(DEFAULT_LOGIN_REDIRECT, nextUrl));
  }

  if (!isLoggedIn && !isPublicRoutes) {
    return NextResponse.redirect(new URL("/auth/login", nextUrl));
  }

  return null;
}

// See "Matching Paths" below to learn more
export const config = {
  matcher: "/about/:path*",
};
