import React from "react";
import GitHubIcon from "@/../public/github-mark-white.svg";
import { Button } from "@nextui-org/button";
import Image from "next/image";
import { signIn } from "next-auth/react";

type Props = {};

const GithubButton = (props: Props) => {
  return (
    <div>
      <Button
        onClick={async () => {
          await signIn("github");
        }}
      >
        <div className="w-8 p-1">
          <Image src={GitHubIcon} alt="github button icon" />
        </div>
        Sign In with GitHub
      </Button>
    </div>
  );
};

export default GithubButton;
