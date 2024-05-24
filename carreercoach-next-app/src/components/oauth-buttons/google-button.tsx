import { Button } from "@nextui-org/button";
import { signIn } from "next-auth/react";
import Image from "next/image";
import GoogleIcon from "@/../public/google-signin.svg";
import React from "react";

type Props = {};

const GoogleButton = (props: Props) => {
  return (
    <div>
      <Button
        onClick={async () => {
          await signIn("google");
        }}
      >
        <div className="w-8 p-1">
          <Image src={GoogleIcon} alt="google button icon" />
        </div>
        <span>Sign In with Google</span>
      </Button>
    </div>
  );
};

export default GoogleButton;
