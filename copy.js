// Adds a "Copy" button to every code block, so install commands can be pasted straight into a
// terminal. Without JavaScript the blocks are plain text that can still be selected.
(() => {
  const copy = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch {
      // Fallback for browsers without the async clipboard (or without permission).
      const t = document.createElement("textarea");
      t.value = text;
      t.style.position = "fixed";
      t.style.opacity = "0";
      document.body.append(t);
      t.select();
      const ok = document.execCommand("copy");
      t.remove();
      return ok;
    }
  };

  document.querySelectorAll("pre").forEach((pre) => {
    // A wrapper holds the button, so it stays put while a long line scrolls sideways.
    const wrap = document.createElement("div");
    wrap.className = "code";
    pre.before(wrap);
    wrap.append(pre);

    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "copy";
    btn.textContent = "Copy";
    btn.setAttribute("aria-label", "Copy to clipboard");
    wrap.append(btn);

    let timer;
    btn.addEventListener("click", async () => {
      // No trailing newline: pasting should never run the last command before you press Enter.
      const ok = await copy(pre.innerText.replace(/\n+$/, ""));
      btn.textContent = ok ? "Copied" : "Press Ctrl+C";
      btn.classList.toggle("done", ok);
      if (!ok) window.getSelection().selectAllChildren(pre);
      clearTimeout(timer);
      timer = setTimeout(() => { btn.textContent = "Copy"; btn.classList.remove("done"); }, 1800);
    });
  });
})();
