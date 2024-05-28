"use client";
import { Textarea } from "@nextui-org/input";
import { Button } from "@nextui-org/react";
import { auth } from "@/auth";
import React from "react";
import { useSession } from "next-auth/react";
import { getUserSession } from "@/lib/auth.actions";
import { IChat } from "@/lib/models/chat.model";

type Props = {
  chat: IChat | null;
};

const ChatInput = (props: Props) => {
  const [message, setMessage] = React.useState("");
  const [chatId, setChatId] = React.useState(null);
  const chat = props.chat;
  const { data: session, status } = useSession();
  const userId = session?.user?._id;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setMessage(e.target.value);
  };

  let url;
  if (!chat) {
    url = "http://localhost:3000/api/chat?new=true";
  } else {
    url = `http://localhost:3000/api/chat?chatId=${chatId}`;
  }

  const sendMessage = async () => {
    try {
      const messageBuilder = {
        content: message,
        sender: "user",
        userId: userId,
      };
      const response = await fetch(url, {
        method: chat ? "PATCH" : "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(messageBuilder),
      });

      if (response.ok) {
        const result = await response.json();
        console.log("Message uploaded Successfully");
        setMessage(""); // Clear the message input after successful upload

        if (!chat) {
          setChatId(result._id);
          localStorage.setItem("currentChatId", result._id);
        }
      } else {
        console.error("Failed to upload message");
      }
    } catch (error) {}
  };

  const handleSend = () => {
    sendMessage();
    setMessage("");
  };

  const SendButton = (
    <Button
      variant="shadow"
      color="primary"
      title="send button"
      isIconOnly
      onClick={handleSend}
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
          d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5"
        />
      </svg>
    </Button>
  );

  return (
    <div className="w-full flex">
      <Textarea
        placeholder="Enter interview question..."
        minRows={1}
        name="message"
        value={message}
        onChange={handleChange}
        endContent={SendButton}
      />
    </div>
  );
};

export default ChatInput;
