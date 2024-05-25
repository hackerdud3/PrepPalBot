import message from "@/components/chat-ui/MessageChip";
import mongoose, { Document, Schema } from "mongoose";

export interface IMessage extends Document {
  sender: string;
  content: string;
  timestamp: Date;
}

const MessageSchema = new mongoose.Schema({
  sender: { type: String, enum: ["user", "bot"], required: true },
  content: { type: String, required: true },
  timestamp: { type: Date, default: Date.now },
});

export interface IChat extends Document {
  userId: mongoose.Types.ObjectId;
  messages: IMessage[];
}

const ChatSchema = new mongoose.Schema({
  userId: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
  messages: [MessageSchema],
});

const Chat = mongoose.models.Chat || mongoose.model<IChat>("Chat", ChatSchema);
const Message =
  mongoose.models.Message || mongoose.model<IMessage>("Message", MessageSchema);

export { Chat, Message };
