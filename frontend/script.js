document.getElementById("intake-form").addEventListener("submit", async function (e) {
  e.preventDefault();

  const name = document.getElementById("name").value;
  const age = document.getElementById("age").value;
  const symptoms = document.getElementById("symptoms").value;

  const responseBox = document.getElementById("ai-response");
  responseBox.innerHTML = `<p>Analyzing symptoms for <strong>${name}</strong>...</p>`;

  try {
    const res = await fetch("https://curly-enigma-xpg6w47-5000.githubpreview.dev/analyze", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ name, age, symptoms }),
    });

    const data = await res.json();
    responseBox.innerHTML = `<p>${data.message}</p>`;
  } catch (error) {
  console.error("❌ Error details:", error);
  responseBox.innerHTML = `<p>Something went wrong: ${error.message}</p>`;
}

});
