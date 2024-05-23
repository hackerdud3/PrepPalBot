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

type Props = {};

const ChatField = (props: Props) => {
  const [message, setMessages] = React.useState([]);

  console.log(message);

  useEffect(() => {
    const fetchMessages = async () => {
      try {
        const response = await fetch("http://localhost:3000/api/message", {
          method: "GET",
        });
        if (response.ok) {
          const data = await response.json();
          setMessages(data);
        } else {
          console.error("Failed to fetch messages");
        }
      } catch (error) {
        console.error("Error fetching messages:", error);
      }
    };

    fetchMessages();
  }, []); // Run only once on component mount

  const createNewConversation = async () => {
    try {
      const response = await fetch("http://localhost:3000/api/conversation", {
        method: "POST",
      });
      if (response.ok) {
        console.log("New conversation created");
      } else {
        console.error("Failed to create new conversation");
      }
    } catch (error) {
      console.error("Error creating new conversation:", error);
    }
  };

  return (
    <div className="h-full">
      <Card className="md:w-[800px] w-[300px] absolute ">
        <CardHeader>
          <div className="flex flex-col">
            <p className="text-md">Chat</p>
            <p className="text-small text-default-500">CareerCoach</p>
          </div>
        </CardHeader>
        <Divider />
        <CardBody className="h-[65vh]">
          <ul>
            {message.map(
              (message: { content: String; sender: String }, index: number) => (
                <li key={index}>{message.content}</li>
              )
            )}
          </ul>
        </CardBody>
        <Divider />
        <CardFooter className="w-full relative flex gap-4">
          <div>
            <Button isIconOnly onClick={createNewConversation}>
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
          <ChatInput />
        </CardFooter>
      </Card>
    </div>
  );
};

export default ChatField;
