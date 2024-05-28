import mongoose, { Types } from "mongoose";
import connectDB from "../mongodb";
import { Chat } from "../models/chat.model";

interface userIdParams {
  userId: string;
}

export async function getAllChats({ userId }: userIdParams) {
  connectDB();
  const objectId = new Types.ObjectId(userId);
  const chats = await Chat.find({ userId: objectId })
    .populate("messages")
    .exec();
  return { chats };
}
