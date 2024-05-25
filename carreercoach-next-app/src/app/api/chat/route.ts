import { NextRequest, NextResponse } from "next/server";
import { Chat, Message } from "@/lib/models/chat.model";
import connectDB from "@/lib/mongodb";

// export async function POST(request: NextRequest) {
//   await connectDB();
//   const { userId, content, sender } = await request.json();
//   const chat = await Chat.create({ userId });
//   return NextResponse.json(chat, { status: 201 });
// }

export async function POST(request: NextRequest) {
  await connectDB();
  const body = await request.json();
  const sender = body.sender;
  const content = body.content;
  const userId = body.userId;
  const chat = await Chat.create({ userId, messages: [{ sender, content }] });
  return NextResponse.json(chat, { status: 201 });
}

export async function GET(request: NextRequest) {
  await connectDB();
  const searchParams = request.nextUrl.searchParams;
  const chatId = "66517a5562bff8d854830b28";
  const chat = await Chat.findById(chatId);
  if (!chat) {
    return NextResponse.json({ error: "Chat not found" }, { status: 404 });
  }
  return NextResponse.json(chat);
}
