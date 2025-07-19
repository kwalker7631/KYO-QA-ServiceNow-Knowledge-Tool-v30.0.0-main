document.getElementById("jobForm")
  .addEventListener("submit", async e => {
    e.preventDefault();
    const status = document.getElementById("status");
    status.textContent = "Processing... please wait.";
    try {
      const resp = await fetch("/api/process", {
        method: "POST",
        body: new FormData(e.target),
      });
      if (!resp.ok) {
        status.textContent = `Error: ${await resp.text()}`;
        return;
      }
      const blob = await resp.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = e.target.excel.files[0].name;
      a.textContent = `Download ${a.download}`;
      status.innerHTML = "";
      status.appendChild(a);
    } catch (err) {
      status.textContent = `Error: ${err.message}`;
    }
  });
