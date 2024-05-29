"use client";
import SideNav from "@/components/navbar/side-nav";
import ChatField from "@/components/chat-ui/ChatField";
import React, { useEffect, useState } from "react";
import { IChat } from "@/lib/models/chat.model";
import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";

const page = ({ params }: { params: { id: string } }) => {
  const { id } = params;

  return (
    <div className="flex px-24 gap-8 h-full">
      <SideNav />
      <div className="h-full">
        <ChatField chatId={id} />
      </div>
    </div>
  );
};
export default page;
