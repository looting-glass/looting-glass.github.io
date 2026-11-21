// Adds a "Copy" button to every code block, so install commands can be pasted straight into a
// terminal. Without JavaScript the blocks are plain text that can still be selected.
(() => {
  // Octicons "copy" and "check" (MIT), the icons GitHub uses for the same button.
  const ICON = '<svg class="icon" viewBox="0 0 16 16" aria-hidden="true"><path d="M0 6.75C0 5.784.784 5 1.75 5h1.5a.75.75 0 0 1 0 1.5h-1.5a.25.25 0 0 0-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 0 0 .25-.25v-1.5a.75.75 0 0 1 1.5 0v1.5A1.75 1.75 0 0 1 9.25 16h-7.5A1.75 1.75 0 0 1 0 14.25Z"/><path d="M5 1.75C5 .784 5.784 0 6.75 0h7.5C15.216 0 16 .784 16 1.75v7.5A1.75 1.75 0 0 1 14.25 11h-7.5A1.75 1.75 0 0 1 5 9.25Zm1.75-.25a.25.25 0 0 0-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 0 0 .25-.25v-7.5a.25.25 0 0 0-.25-.25Z"/></svg>';
  const CHECK = '<svg class="check" viewBox="0 0 16 16" aria-hidden="true"><path d="M13.78 4.22a.75.75 0 0 1 0 1.06l-7.25 7.25a.75.75 0 0 1-1.06 0L2.22 9.28a.751.751 0 0 1 .018-1.042.751.751 0 0 1 1.042-.018L6 10.94l6.72-6.72a.75.75 0 0 1 1.06 0Z"/></svg>';

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
    btn.title = "Copy";
    btn.setAttribute("aria-label", "Copy to clipboard");
    btn.innerHTML = ICON + CHECK;
    wrap.append(btn);

    let timer;
    btn.addEventListener("click", async () => {
      // No trailing newline: pasting should never run the last command before you press Enter.
      const ok = await copy(pre.innerText.replace(/\n+$/, ""));
      btn.classList.toggle("done", ok);
      btn.title = ok ? "Copied!" : "Press Ctrl+C to copy";
      if (!ok) window.getSelection().selectAllChildren(pre);
      clearTimeout(timer);
      timer = setTimeout(() => { btn.classList.remove("done"); btn.title = "Copy"; }, 1800);
    });
  });
})();
