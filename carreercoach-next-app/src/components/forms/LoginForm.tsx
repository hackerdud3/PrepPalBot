"use client";
import React, { FormEvent } from "react";
import { Input } from "@nextui-org/input";
import { Button } from "@nextui-org/button";
import { Card, CardBody, Link } from "@nextui-org/react";
import * as z from "zod";
import { userSignInValidation } from "@/lib/validations/auth";
import Image from "next/image";
import GoogleButton from "../oauth-buttons/google-button";
import GithubButton from "../oauth-buttons/github-button";
import { useRouter } from "next/navigation";

type Props = {};

export default function LoginForm(prop: Props) {
  const [isLoading, setLoading] = React.useState(false);
  const router = useRouter();

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const formData = new FormData(event.currentTarget);
    const email = formData.get("email") as string;
    const password = formData.get("pasword") as string;

    try {
      const response = await fetch("/api/auth/signin", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      if (response.ok) {
        console.log("successfully logged in");
        router.push("/");
      }
    } catch (error) {}
  }

  return (
    <form onSubmit={handleSubmit}>
      <Card className=" lg:w-[500px] p-6 min-w-[350px] ">
        <CardBody className="flex flex-col gap-6">
          <Input placeholder="Enter your email" type="email" name="email" />
          <Input placeholder="********" type="password" name="password" />
          <div className="flex flex-col items-center justify-center gap-4">
            <Button
              color="primary"
              isLoading={isLoading}
              className="w-32 flex-grow"
              type="submit"
            >
              Login
            </Button>
            <Link size="sm" underline="hover" href="#">
              Forgot password?
            </Link>
          </div>

          <div className="flex lg:flex-row justify-between gap-2 items-center flex-col">
            <GoogleButton />
            <GithubButton />
          </div>
        </CardBody>
      </Card>
    </form>
  );
}
