import mongoose, { Document, Schema } from "mongoose";

// Define the schema for the Message model
export interface IMessage extends Document {
  sender: string;
  content: string;
  timestamp: Date;
}

const messageSchema = new Schema({
  sender: { type: String, required: true },
  content: { type: String, required: true },
  timestamp: { type: Date, default: Date.now },
});

const Message = mongoose.model<IMessage>("Message", messageSchema);

export interface IConversation extends Document {
  userId: mongoose.Types.ObjectId;
  messages: IMessage[];
}

const conversationSchema = new Schema({
  userId: { type: Schema.Types.ObjectId, required: true },
  messages: [messageSchema],
});

const Conversation = mongoose.model<IConversation>(
  "Conversation",
  conversationSchema
);

export { Conversation, Message };
