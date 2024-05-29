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
  const [messages, setMessages] = useState<IMessage[]>(chat?.messages || []);
  const router = useRouter();
  const { data: session, status } = useSession();
  console.log(messages);

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
    <div className="h-full w-full pr-6">
      <Card className="w-full h-full" radius="sm">
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
        <CardBody className="flex-grow overflow-auto flex justify-start items-center">
          <ScrollShadow hideScrollBar orientation="horizontal">
            {messages?.map((item) => (
              <div className="w-[850px]" key={item?._id}>
                <MessageChip message={item?.content} sender={item?.sender} />
              </div>
            ))}
          </ScrollShadow>
        </CardBody>
        <div className="px-4 pb-6 m-2">
          <ChatInput chat={chat} setMessages={setMessages} />
        </div>
      </Card>
    </div>
  );
};

export default ChatField;
