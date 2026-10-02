import "dotenv/config";
import app from "./app.js";
import { initializeDataStore } from "./config/database.js";

const port = Number(process.env.PORT) || 5000;
const host = process.env.HOST || "127.0.0.1";

initializeDataStore();

app.listen(port, host, () => {
  console.log(`===================================================`);
  console.log(`OneSpace Express API: http://${host}:${port}`);
  console.log(`OneSpace Web App:     http://onespace.local`);
  console.log(`===================================================`);
});
