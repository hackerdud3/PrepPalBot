"use client";
import { ListBoxWrapper } from "@/components/chat-ui/ListBoxWrapper";
import { IChat } from "@/lib/models/chat.model";
import { Chip, Listbox, ListboxItem, ScrollShadow } from "@nextui-org/react";
import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import React, { useEffect, useState } from "react";

Listbox;

export default function Home() {
  const [chats, setChats] = React.useState<IChat[]>([]);
  const [selectedKeys, setSelectedKeys] = useState<Set<string>>(new Set(["1"]));
  const [currentChat, setCurrentChat] = useState<IChat>(chats[0] || null);

  const router = useRouter();

  const { data: session, status } = useSession();
  console.log(session?.user?._id);

  const selectedValue = React.useMemo(
    () => Array.from(selectedKeys).join(", "),
    [selectedKeys]
  );

  const handleSelectionChange = (keys: any) => {
    // Ensure the keys parameter is a Set<string>
    setSelectedKeys(new Set(keys));
  };

  const selectChat = (chatId: string) => {
    router.push(`/chat/${chatId}`);
  };

  useEffect(() => {
    const fetchChats = async () => {
      // Check if the session is loaded and the user is authenticated
      if (status === "authenticated") {
        const userId = session?.user?._id;

        // Check if userId exists before making the fetch request
        if (userId) {
          try {
            const response = await fetch(`/api/chat?userId=${userId}`);
            const data = await response.json();
            setChats(data.chats || null);
          } catch (error) {
            console.error("Unable to fetch chats:", error);
          }
        } else {
          console.error("User ID not found in session.");
          // Handle the case where userId is missing (e.g., show an error message)
        }
      }
    };

    fetchChats();
  }, [session?.user]);

  // Rest of your component logic (listbox and chip rendering)

  return (
    <main className="inset-0 flex items-center justify-center ">
      <ListBoxWrapper>
        <ScrollShadow hideScrollBar className="w-full h-full">
          <Listbox
            classNames={{
              list: "h-full",
            }}
            items={chats}
            selectedKeys={selectedKeys}
            onSelectionChange={handleSelectionChange}
            selectionMode="single"
            variant="flat"
          >
            {chats?.map((item) => (
              <ListboxItem
                key={item?._id}
                className="h-12"
                onClick={() => selectChat(item?._id)}
              >
                <span>{item?.messages[0]?.content}</span>
              </ListboxItem>
            ))}
          </Listbox>
        </ScrollShadow>
      </ListBoxWrapper>
    </main>
  );
}
