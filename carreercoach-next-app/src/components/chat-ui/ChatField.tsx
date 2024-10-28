"use client";
import {
  Button,
  Card,
  CardBody,
  CardFooter,
  CardHeader,
  Divider,
  ScrollShadow,
  Textarea,
} from "@nextui-org/react";
import React, { useEffect, useState } from "react";

import ChatInput from "./ChatInput";
import { IChat, IMessage } from "@/lib/models/chat.model";
import MessageChip from "./MessageChip";
import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";

type Props = {
  chatId: string;
};

const ChatField = (props: Props) => {
  const { chatId } = props;
  const [chat, setChat] = React.useState<IChat | null>(null);
  const [messages, setMessages] = useState<IMessage[]>();

  const router = useRouter();
  const { data: session, status } = useSession();

  useEffect(() => {
    const fetchChat = async (chatId: string) => {
      try {
        const response = await fetch(`/api/chat/${chatId}`, { method: "GET" });
        if (response.ok) {
          const data = await response.json();
          setChat(data?.chat);
          setMessages(data?.chat?.messages);
        } else {
          console.error("Failed to fetch chat");
        }
      } catch (error) {
        console.error("Error fetching chat:", error);
      }
    };

    if (chatId !== "new" && status === "authenticated") {
      fetchChat(chatId);
    }
  }, [chatId, status]);

  const handleCreateNewChat = () => {
    router.push("/chat/new");
    setChat(null);
  };

  return (
    <Card className="w-full h-full">
      <CardHeader className="flex justify-between">
        <div className="flex flex-col">
          <p className="text-md">Chat</p>
          <p className="text-small text-default-500">CareerCoach</p>
        </div>
        <div className="flex gap-2 items-center justify-center">
          <span>Create new chat</span>
          <Button isIconOnly onClick={handleCreateNewChat}>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
              className="w-6 h-6"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M12 4.5v15m7.5-7.5h-15"
              />
            </svg>
          </Button>
        </div>
      </CardHeader>
      <Divider />
      <CardBody className="flex-1 max-w-[40rem] overflow-auto mx-auto">
        <ScrollShadow hideScrollBar orientation="horizontal">
          {messages?.map((item) => (
            <div key={item?._id}>
              <MessageChip message={item?.content} sender={item?.sender} />
            </div>
          ))}
        </ScrollShadow>
      </CardBody>
      <div className="p-2 m-2">
        <ChatInput chat={chat} setMessages={setMessages} />
      </div>
    </Card>
  );
};

export default ChatField;
