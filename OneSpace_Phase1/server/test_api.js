import app from "./src/app.js";

const server = app.listen(0, async () => {
  const port = server.address().port;
  console.log(`Test server running on port ${port}`);

  try {
    const healthRes = await fetch(`http://localhost:${port}/api/health`);
    const healthData = await healthRes.json();
    console.log("Health Check:", JSON.stringify(healthData));

    const itemsRes = await fetch(`http://localhost:${port}/api/items`);
    const itemsData = await itemsRes.json();
    console.log(`GET /api/items count: ${itemsData.data?.length}`);

    const spacesRes = await fetch(`http://localhost:${port}/api/spaces`);
    const spacesData = await spacesRes.json();
    console.log(`GET /api/spaces count: ${spacesData.data?.length}`);

    console.log("ALL API TESTS PASSED SUCCESSFULLY!");
  } catch (err) {
    console.error("API Test Error:", err);
  } finally {
    server.close();
    process.exit(0);
  }
});
