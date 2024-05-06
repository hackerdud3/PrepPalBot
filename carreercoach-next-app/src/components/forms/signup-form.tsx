"use client";
import React from "react";
import { Input } from "@nextui-org/input";
import { Button } from "@nextui-org/button";
import { useState } from "react";
import { Card, CardBody, Link } from "@nextui-org/react";
import { useSession } from "next-auth/react";
import * as z from "zod";
import { userSignUpValidation } from "@/lib/validations/auth";
import { signUpWithCredentials } from "@/lib/actions/auth.actions";
import { signIn } from "next-auth/react";
import { useRouter } from "next/navigation";

type Props = {};

const SignUpForm = (prop: Props) => {
  const [isLoading, setLoading] = React.useState(false);
  const { data: session } = useSession();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");

  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    const values = {
      email,
      password,
      name,
    };
    const res = await signUpWithCredentials(values);

    if (res?.success) {
      console.log("success");
      router.push("/signin");
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    const { name, value } = e.target as HTMLInputElement;
    if (name === "email") {
      setEmail(value);
    } else if (name === "name") {
      setName(value);
    } else {
      setPassword(value);
    }
  };

  return (
    <>
      <form onSubmit={handleSubmit}>
        <Card className=" md:w-[500px] p-6 w-[300px]">
          <CardBody className="flex flex-col gap-6">
            <Input
              name="name"
              value={name}
              placeholder="name"
              onChange={handleChange}
            />
            <Input
              placeholder="Enter your email"
              type="email"
              name="email"
              value={email}
              onChange={handleChange}
            />
            <Input
              placeholder="Password"
              type="passwordd"
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
                Sign Up
              </Button>
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
    </>
  );
};

export default SignUpForm;
