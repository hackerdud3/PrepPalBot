import { strict } from "assert";
import mongoose from "mongoose";
import { MongooseOptions } from "mongoose";
import { version } from "os";
const connection: { isConnected?: number } = {};

const clientOptions = {
  serverApi: { version: "1", strict: true, deprecationErrors: true },
};

const connectDB = async () => {
  try {
    await mongoose.connect(
      process.env.MONGODB_URI as string,
      clientOptions as mongoose.ConnectOptions
    );
    await mongoose.connection.db.admin().command({ ping: 1 });
    console.log("MongoDB connected");
  } catch (error) {
    console.log("MongoDB connection failed", (error as Error).message);
  }
};
export default connectDB;
