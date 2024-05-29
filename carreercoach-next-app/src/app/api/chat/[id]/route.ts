import { Chat, IChat, IMessage, Message } from "@/lib/models/chat.model";
import connectDB from "@/lib/mongodb";
import { nextauthOptions } from "@/lib/nextauth-options";
import { ObjectId } from "mongodb";
import { Types } from "mongoose";
import { getServerSession } from "next-auth";
import { NextRequest, NextResponse } from "next/server";

interface Params {
  id: string;
}
export async function GET(
  request: NextRequest,
  { params }: { params: Params }
) {
  // Extract chatId from the URL directly
  const chatId = params.id;

  if (!ObjectId.isValid(chatId)) {
    return NextResponse.json({ error: "Invalid Chat ID" }, { status: 400 });
  }

  try {
    await connectDB();
    const chat: IChat | null = await Chat.findById(chatId);

    if (!chat) {
      return NextResponse.json({ error: "No chat found" }, { status: 404 });
    }

    return NextResponse.json({ chat });
  } catch (error) {
    console.error("Error fetching chat:", error);
    return NextResponse.json({ error: "Error fetching chat" }, { status: 500 });
  }
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: Params }
) {
  const chatId = params.id;
  if (!ObjectId.isValid(chatId)) {
    return NextResponse.json({ error: "Invalid Chat ID" }, { status: 400 });
  }
  const body = await request.json();
  const { sender, content } = body;

  if (!sender || !content) {
    return NextResponse.json(
      { error: "Missing required fields" },
      { status: 400 }
    );
  }

  try {
    connectDB();
    const chat: IChat | null = await Chat.findById(chatId);
    if (!chat) {
      return NextResponse.json({ error: "Chat not found" }, { status: 404 });
    }
    const message: IMessage = new Message({ sender, content });
    chat.messages.push(message);
    await chat.save();

    return NextResponse.json({ message: message });
  } catch (error) {
    return NextResponse.json(
      { error: "Error sending message" },
      { status: 500 }
    );
  }
}
