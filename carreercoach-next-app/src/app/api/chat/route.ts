import { NextRequest, NextResponse } from "next/server";
import { Chat, IChat, Message } from "@/lib/models/chat.model";
import connectDB from "@/lib/mongodb";
import { isUtf8 } from "buffer";
import { error } from "console";
import { Content } from "next/font/google";
import { getServerSession } from "next-auth";
import { nextauthOptions } from "@/lib/nextauth-options";
import { getAllChats } from "@/lib/actions/chat.actions";
import { Types } from "mongoose";

// export async function POST(request: NextRequest) {
//   await connectDB();
//   const { userId, content, sender } = await request.json();
//   const chat = await Chat.create({ userId });
//   return NextResponse.json(chat, { status: 201 });
// }

export async function POST(request: NextRequest) {
  await connectDB();
  const searchParams = request.nextUrl.searchParams;
  let isTrue = false;
  if (searchParams.get("new") === "true") {
    isTrue = true;
  }
  const body = await request.json();
  const { sender, content, userId } = body;

  if (!sender || !content || !userId) {
    return NextResponse.json(
      { error: "Missing required fields" },
      { status: 400 }
    );
  }

  let chat = null;
  if (isTrue) {
    const message = new Message({ sender, content });
    chat = await Chat.create({ userId, messages: [message] });
  }
  return NextResponse.json({ message: chat.messages[0] }, { status: 201 });
}

export async function GET(request: NextRequest) {
  await connectDB();

  const searchParam = request.nextUrl.searchParams;
  const userId = searchParam?.get("userId");
  if (!userId) {
    return new NextResponse("Unauthorized", { status: 401 });
  }
  try {
    const chats = await getAllChats({ userId });
    return NextResponse.json(chats);
  } catch (error) {
    // Handle invalid ObjectId format (e.g., return a 400 Bad Request error)
    return NextResponse.json(
      { error: "Error fetching chats" },
      { status: 400 }
    );
  }
}
