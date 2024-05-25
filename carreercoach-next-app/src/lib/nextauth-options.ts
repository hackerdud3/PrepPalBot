import { NextAuthOptions } from "next-auth";
import Google from "next-auth/providers/google";
import Credentials from "next-auth/providers/credentials";
import {
  signInWithOauth,
  getUserByEmail,
  signInWithCredentials,
} from "@/lib/auth.actions";
import Github from "next-auth/providers/github";

export const providers = [
  Google({
    clientId: process.env.AUTH_GOOGLE_CLIENT_ID!,
    clientSecret: process.env.AUTH_GOOGLE_SECRET!,
  }),
  Github({
    clientId: process.env.AUTH_GITHUB_CLIENT_ID!,
    clientSecret: process.env.AUTH_GITHUB_SECRET!,
  }),
  Credentials({
    name: "Credentials",
    credentials: {
      email: { label: "Email", type: "email", required: true },
      password: { label: "Password", type: "password", required: true },
    },
    async authorize(credentials) {
      if (!credentials?.email || !credentials?.password) {
        return null;
      }
      const user = await signInWithCredentials({
        email: credentials?.email,
        password: credentials?.password,
      });
      return user;
    },
  }),
];

export const nextauthOptions: NextAuthOptions = {
  secret: process.env.NEXTAUTH_SECRET,
  pages: {
    signIn: "/signin",
    error: "/error",
    signOut: "/signout",
  },
  providers: providers,
  callbacks: {
    async signIn({ account, profile }) {
      // console.log({account, profile})
      if (account?.type === "oauth" && profile) {
        return await signInWithOauth({ account, profile });
      }
      return true;
    },
    async jwt({ token, trigger, session }) {
      // console.log({token})
      // console.log({trigger, session})
      if (trigger === "update") {
        token.name = session.name;
      } else {
        if (token.email) {
          const user = await getUserByEmail({ email: token.email });
          // console.log({user})
          token.name = user.name;
          token._id = user._id;
          token.role = user.role;
          token.provider = user.provider;
        }
      }
      return token;
    },
    async session({ session, token }) {
      // console.log({session, token})
      return {
        ...session,
        user: {
          ...session.user,
          name: token.name,
          _id: token._id,
          role: token.role,
          provider: token.provider,
        },
      };
    },
  },
};
