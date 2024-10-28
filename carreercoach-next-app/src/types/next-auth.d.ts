import NextAuth from "next-auth";

declare module "next-auth" {
  interface User {
    _id: string;
    role: string;
    provider: string;
  }
  interface Session {
    user: User & {
      name: string;
      email: string;
      image: string;
    };
    token: {
      _id: string;
      role: string;
      provider: string;
    };
  }
}
