import mongoose from "mongoose";

mongoose.set("bufferCommands", false);

let isDbConnected = false;

export function isConnected() {
  return isDbConnected && mongoose.connection.readyState === 1;
}

export function initializeDataStore() {
  const uri = process.env.MONGODB_URI;
  if (uri) {
    // Ultra-fast 200ms background connection check
    mongoose.connect(uri, {
      serverSelectionTimeoutMS: 200,
      connectTimeoutMS: 200
    }).then(() => {
      isDbConnected = true;
      console.log("MongoDB connected.");
    }).catch(() => {
      isDbConnected = false;
    });
  }
  return true;
}
