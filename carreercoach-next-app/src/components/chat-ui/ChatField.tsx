"use client";
import {
  Button,
  Card,
  CardBody,
  CardFooter,
  CardHeader,
  Divider,
} from "@nextui-org/react";
import React, { useEffect } from "react";

import ChatInput from "./ChatInput";
import { IChat } from "@/lib/models/chat.model";

type Props = {
  chatId: string;
};

const ChatField = (props: Props) => {
  const [messages, setMessages] = React.useState([]);
  const [chat, setChat] = React.useState<IChat | null>(null);

  useEffect(() => {
    const fetchChat = async (chatId: string) => {
      try {
        const response = await fetch(
          `http://localhost:3000/api/chat?chatId=${chatId}`,
          {
            method: "GET",
          }
        );
        if (response.ok) {
          const data = await response.json();
          setChat(data);
        } else {
          console.error("Failed to fetch chat");
        }
      } catch (error) {
        console.error("Error fetching messages:", error);
      }
    };
    const chatId = localStorage.getItem("currentChatId");
    if (chatId) {
      fetchChat(chatId);
    }
  }, []); // Run only once on component mount

  return (
    <div className="h-full">
      <Card className="md:w-[800px] w-[300px] absolute ">
        <CardHeader className="flex justify-between">
          <div className="flex flex-col">
            <p className="text-md">Chat</p>
            <p className="text-small text-default-500">CareerCoach</p>
          </div>
          <div className="flex gap-2 items-center justify-center">
            <span>Create new chat</span>
            <Button
              isIconOnly
              onClick={() => {
                setChat(null);
              }}
            >
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
        <CardBody className="h-[65vh]"></CardBody>
        <Divider />
        <CardFooter className="w-full relative flex gap-4">
          <ChatInput chat={chat} />
        </CardFooter>
      </Card>
    </div>
  );
};

export default ChatField;
