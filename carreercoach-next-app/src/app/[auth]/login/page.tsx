import React from "react";
import { Input } from "@nextui-org/input";

type Props = {};

const page = (props: Props) => {
  return (
    <div>
      <div>
        <Input label="Email" type="email" placeholder="Enter your email" />
        <Input label="Password" type="password" placeholder="Password" />
      </div>
    </div>
  );
};

export default page;
