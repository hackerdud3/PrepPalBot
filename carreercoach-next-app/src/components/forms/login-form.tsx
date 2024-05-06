"use client";
import React from "react";
import { Input } from "@nextui-org/input";
import { Button } from "@nextui-org/button";
import { useState } from "react";
import { Card, CardBody, Link } from "@nextui-org/react";
import { signIn, useSession } from "next-auth/react";
import * as z from "zod";
import { userSignInValidation } from "@/lib/validations/auth";

type Props = {};

const LoginForm = (prop: Props) => {
  const [isLoading, setLoading] = React.useState(false);
  const { data: session } = useSession();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    try {
      const user = await signIn("credentials", {
        email,
        password,
        callbackUrl: "/",
      });

      console.log(user);
    } catch (error) {
      console.log(error);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    const { name, value } = e.target as HTMLInputElement;
    if (name === "email") {
      setEmail(value);
    } else {
      setPassword(value);
    }
  };

  return (
    <>
      {/* {!session ? ( */}
      <form onSubmit={handleSubmit}>
        <Card className=" w-[500px] p-6">
          <CardBody className="flex flex-col gap-6">
            <Input
              placeholder="Enter your email"
              type="email"
              name="email"
              value={email}
              onChange={handleChange}
            />
            <Input
              placeholder="Passord"
              type="password"
              name="password"
              value={password}
              onChange={handleChange}
            />
            <div className="flex items-center justify-center gap-4">
              <Button
                color="primary"
                isLoading={isLoading}
                className="w-32"
                type="submit"
              >
                Login
              </Button>
              <Link
                size="sm"
                underline="hover"
                href="#"
                className=" absolute right-8"
              >
                Forgot password?
              </Link>
            </div>

            <Button
              onClick={async () => {
                await signIn("google");
              }}
              color="primary"
            >
              Sign In with Google
            </Button>

            <Button
              onClick={async () => {
                await signIn("github");
              }}
              color="primary"
            >
              Sign In with Github
            </Button>
          </CardBody>
        </Card>
      </form>
      {/* ) : (
        <div>Logged in</div>
      )} */}
    </>
  );
};

export default LoginForm;
