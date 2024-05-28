"use client";
import React, { useEffect, useState } from "react";

export default function Home() {
  const [chats, setChats] = React.useState([]);

  useEffect(() => {
    const fetchChats = async () => {
      try {
        const response = await fetch("/api/chat");
        const data = await response.json();
        setChats(data);
      } catch (error) {
        console.log("Unablel to fetch chats");
      }
    };
    fetchChats();
  }, []);
  return;
  <main className="inset-0 flex items-center justify-center"></main>;
}
