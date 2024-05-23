import { Conversation, Message } from "@/lib/models/conversation.model";
import connectDB from "@/lib/mongodb";
import { NextApiRequest, NextApiResponse } from "next";
import { NextRequest } from "next/server";

export async function GET(request: NextRequest) {
  await connectDB();
  const searchParams = request.nextUrl.searchParams;
  const conversationId = searchParams.get("conversationId");
  const conversation = await Conversation.findById("663b0a1034a1f9f42ac9de22");
  const messages = conversation?.messages;
  return new Response(JSON.stringify(messages), { status: 200 });
}

export async function POST(request: NextRequest) {
  await connectDB();
  const searchParams = request.nextUrl.searchParams;
  const conversationId = searchParams.get("conversationId");
  let conversation = await Conversation.findById(conversationId);

  if (!conversation) {
    conversation = new Conversation({ _id: conversationId, messages: [] });
    await conversation.save();
  }

  // Extract the message data from the request body
  const { content, sender } = await request.json();

  // Check for missing fields in request body (optional)
  if (!content || !sender) {
    return new Response("Missing fields in request body", { status: 400 });
  }

  // Create a new message instance based on the Message schema
  const newMessage = new Message({ content, sender });

  // Save the new message to the database
  const savedMessage = await newMessage.save();

  // Push the saved message ID to the conversation's messages array
  conversation.messages.push(savedMessage);
  await conversation.save();

  return new Response(JSON.stringify(savedMessage), { status: 200 });
}
