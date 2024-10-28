import { NextRequest } from "next/server";
import { auth } from "./auth";
import {
  apiAuthPrefix,
  DEFAULT_LOGIN_REDIRECT,
  authRoutes,
  publicRoutes,
} from "./lib/protected-routes";

export function middleware(request: NextRequest) {
  const { nextUrl } = request;
}
