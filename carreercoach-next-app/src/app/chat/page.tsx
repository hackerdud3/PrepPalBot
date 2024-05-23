"use client";
import SideNav from "@/components/navbar/side-nav";
import ChatField from "@/components/chat-ui/ChatField";
import { NextPage } from "next";
import { useRouter } from "next/navigation";

import React, { useEffect } from "react";

const Page: NextPage = () => {
  return (
    <div className="flex px-24 gap-8 relative h-full">
      <SideNav />
      <div>
        <ChatField />
      </div>
    </div>
  );
};

export default Page;
