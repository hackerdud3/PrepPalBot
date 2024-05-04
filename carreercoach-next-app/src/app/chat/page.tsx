import SideNav from "@/components/Navbar/side-nav";
import { Navbar } from "@nextui-org/navbar";
import React from "react";

type Props = {};

const page = (props: Props) => {
  return (
    <div className="flex h-[90vh] px-6 relative">
      <SideNav />
      <div>Body</div>
    </div>
  );
};

export default page;
