"use client";
import React, { FormEvent } from "react";
import GitHubIcon from "@/../public/github-mark-white.svg";
import { Input } from "@nextui-org/input";
import { Button } from "@nextui-org/button";
import { useState } from "react";
import { Card, CardBody, Link } from "@nextui-org/react";
import { signIn } from "next-auth/react";
import * as z from "zod";
import { userSignInValidation } from "@/lib/validations/auth";
import Image from "next/image";
import GoogleButton from "../oauth-buttons/google-button";
import GithubButton from "../oauth-buttons/github-button";

type Props = {};

const LoginForm = (prop: Props) => {
  const [isLoading, setLoading] = React.useState(false);

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
      }
    } catch (error) {}
  }

  return (
    <>
      <form onSubmit={handleSubmit}>
        <Card className=" w-[500px] p-6">
          <CardBody className="flex flex-col gap-6">
            <Input placeholder="Enter your email" type="email" name="email" />
            <Input placeholder="********" type="password" name="password" />
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

            <div className="flex justify-between gap-x-4 items-center">
              <GoogleButton />
              <GithubButton />
            </div>
          </CardBody>
        </Card>
      </form>
    </>
  );
};

export default LoginForm;
