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
    <div className="flex px-4 m-4 gap-8 h-full">
      <div className="min-w-[350px] flex-shrink-0 h-full overflow-x-hidden ">
        <SideNav />
      </div>
      <div className="h-full w-full flex-1 flex justify-start items-center">
        <ChatField chatId={id} />
      </div>
    </div>
  );
};
export default page;
