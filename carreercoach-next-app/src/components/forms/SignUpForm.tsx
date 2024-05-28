"use client";
import React from "react";
import { Input } from "@nextui-org/input";
import { Button } from "@nextui-org/button";
import { useState } from "react";
import { Card, CardBody, Link } from "@nextui-org/react";
import { useSession } from "next-auth/react";
import * as z from "zod";
import { userSignUpValidation } from "@/lib/validations/auth";
import { signIn } from "next-auth/react";
import { useRouter } from "next/navigation";
import GoogleButton from "../oauth-buttons/google-button";
import GithubButton from "../oauth-buttons/github-button";
import { signUpWithCredentials } from "@/lib/auth.actions";

type Props = {};

const SignUpForm = (prop: Props) => {
  const [isLoading, setLoading] = React.useState(false);

  const router = useRouter();

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const formData = new FormData(event.currentTarget);
    const name = formData.get("name") as string;
    const email = formData.get("email") as string;
    const password = formData.get("password") as string;

    const values = {
      name,
      email,
      password,
    };
    try {
      const response = await signUpWithCredentials(values);

      if (response?.success) {
        console.log("successfully registered");
        router.push("/signin");
      }
    } catch (error) {
      console.error("Error signing up:", error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <Card className=" md:w-[500px] p-6 min-w-[350px]">
        <CardBody className="flex flex-col gap-6">
          <Input name="name" placeholder="Enter your name" />
          <Input placeholder="Enter your email" type="email" name="email" />
          <Input placeholder="*********" type="password" name="password" />
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
          <div className="flex justify-between gap-2 lg:flex-row flex-col items-center">
            <GoogleButton />
            <GithubButton />
          </div>
        </CardBody>
      </Card>
    </form>
  );
};
export default SignUpForm;
