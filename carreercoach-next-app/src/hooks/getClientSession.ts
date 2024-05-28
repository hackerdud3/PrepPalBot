import { useSession } from "next-auth/react";

export function getClientSession() {
  const { data: session, status } = useSession();
  if (status !== "authenticated") {
    return null;
  }
  return session;
}
