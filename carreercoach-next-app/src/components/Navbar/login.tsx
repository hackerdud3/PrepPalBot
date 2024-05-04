"use client";
import React from "react";
import { Input } from "@nextui-org/input";
import { Button } from "@nextui-org/button";
import { useState } from "react";
import { Card, CardBody, Link } from "@nextui-org/react";
import { signIn, useSession } from "next-auth/react";

type Props = {};

const Login = (prop: Props) => {
  const [isLoading, setLoading] = React.useState(false);
  const { data: session } = useSession();

  return (
    <>
      {!session ? (
        <Card className=" w-[500px] p-6">
          <CardBody className="flex flex-col gap-6">
            <Input placeholder="Enter your email" type="email" />
            <Input placeholder="Passord" type="passwordd" />
            <div className="flex items-center justify-center gap-4">
              <Button color="primary" isLoading={isLoading} className="w-32">
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
          </CardBody>
        </Card>
      ) : (
        <div>Logged in</div>
      )}
    </>
  );
};

export default Login;
