import { Conversation, Message } from "@/lib/models/conversation.model";
import connectDB from "@/lib/mongodb";
import { NextRequest } from "next/server";

export async function GET() {}

export async function POST(request: NextRequest) {
  await connectDB();
  const newMessage = new Message({ content: "Hello", sender: "User" });

  const conversation = Conversation.create({ messages: [newMessage] });
}
