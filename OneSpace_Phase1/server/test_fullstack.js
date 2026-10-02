async function test() {
  try {
    const res = await fetch("http://localhost:5000");
    const text = await res.text();
    console.log(`Server Status: ${res.status}`);
    console.log(`HTML Length: ${text.length}`);
    console.log(`Includes OneSpace: ${text.includes("OneSpace")}`);
    process.exit(0);
  } catch (err) {
    console.error("Fetch Error:", err);
    process.exit(1);
  }
}

test();
