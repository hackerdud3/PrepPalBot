"use client";
import { Textarea } from "@nextui-org/input";
import { Button } from "@nextui-org/react";

import React from "react";

type Props = {};

const ChatInput = (props: Props) => {
  const [message, setMessage] = React.useState("");

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setMessage(e.target.value);
  };

  const uploadMessage = async () => {
    try {
      const messageBuilder = {
        content: message,
        sender: "user",
      };
      const response = await fetch(
        "http://localhost:3000/api/message?conversationId=663b0a1034a1f9f42ac9de22",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(messageBuilder),
        }
      );

      if (response.ok) {
        console.log("Message uploaded successfully");
        setMessage(""); // Clear the message input after successful upload
      } else {
        console.error("Failed to upload message");
      }
    } catch (error) {}
  };

  const handleSend = () => {
    uploadMessage();
    setMessage("");
  };

  return (
    <div className="w-full flex">
      <Textarea
        placeholder="Enter interview question..."
        minRows={1}
        name="message"
        value={message}
        onChange={handleChange}
        endContent={
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
        }
      />
    </div>
  );
};

export default ChatInput;
