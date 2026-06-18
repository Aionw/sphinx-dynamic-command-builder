(() => {
  function tokenizeCommand(command) {
    return command.match(/"[^"]*"|'[^']*'|\S+/g) || [];
  }

  function splitCommandParts(command) {
    const tokens = tokenizeCommand(command);
    const firstOption = tokens.findIndex((token) => token.startsWith("--"));

    if (firstOption === -1) {
      return {
        prefix: tokens.join(" "),
        options: [],
      };
    }

    return {
      prefix: tokens.slice(0, firstOption).join(" "),
      options: groupOptionTokens(tokens.slice(firstOption)),
    };
  }

  function groupOptionTokens(tokens) {
    const groups = [];
    let group = [];

    tokens.forEach((token) => {
      if (token.startsWith("--") && group.length) {
        groups.push(group.join(" "));
        group = [token];
        return;
      }

      group.push(token);
    });

    if (group.length) {
      groups.push(group.join(" "));
    }

    return groups;
  }

  function formatCommand(env, command, args, config) {
    if (config.lineBreak === "none") {
      return [...env, command, ...args].filter(Boolean).join(" ");
    }

    const commandParts = splitCommandParts(command);
    const lines = [
      ...env.map((line) => ({ text: line, indent: false })),
      { text: commandParts.prefix, indent: false },
      ...commandParts.options.map((line) => ({ text: line, indent: true })),
      ...args
        .flatMap((arg) => groupOptionTokens(tokenizeCommand(arg)))
        .map((line) => ({ text: line, indent: true })),
    ].filter((line) => line.text);

    return lines
      .map((line, index) => {
        const continuation = index < lines.length - 1 ? " \\" : "";
        const indent = line.indent ? config.indent : "";
        return `${indent}${line.text}${continuation}`;
      })
      .join("\n");
  }

  function escapeHtml(value) {
    return value.replace(/[&<>"']/g, (character) => {
      const entities = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
      };
      return entities[character];
    });
  }

  function highlightCommandLine(line) {
    const tokenPattern = /(\\|--[A-Za-z0-9][A-Za-z0-9-]*|\[[^\]]+\]|\b[A-Za-z_][A-Za-z0-9_]*=[^\s\\]+)/g;

    return escapeHtml(line).replace(tokenPattern, (token) => {
      if (token === "\\") {
        return '<span class="sdc-token-continuation">\\</span>';
      }
      if (token.startsWith("--")) {
        return `<span class="sdc-token-option">${token}</span>`;
      }
      if (token.startsWith("[") && token.endsWith("]")) {
        return `<span class="sdc-token-placeholder">${token}</span>`;
      }
      if (/^[A-Za-z_][A-Za-z0-9_]*=/.test(token)) {
        return `<span class="sdc-token-env">${token}</span>`;
      }
      return token;
    });
  }

  function highlightCommand(output) {
    output.innerHTML = output.textContent.split("\n").map(highlightCommandLine).join("\n");
  }

  function refreshHighlighting(output) {
    if (window.Prism?.highlightElement) {
      window.Prism.highlightElement(output);
      return true;
    }

    if (window.hljs?.highlightElement) {
      window.hljs.highlightElement(output);
      return true;
    }

    return false;
  }

  function readState(panel) {
    const keys = Array.from(
      new Set(
        Array.from(panel.querySelectorAll("[data-sdc-option]")).map((option) =>
          option.getAttribute("data-sdc-option")
        )
      )
    );

    return keys.reduce((state, key) => {
      const selected = panel.querySelector(
        `[data-sdc-option="${key}"][data-sdc-default="true"]`
      );
      const first = panel.querySelector(`[data-sdc-option="${key}"]`);
      state[key] = (selected || first)?.getAttribute("data-sdc-value") || "";
      return state;
    }, {});
  }

  function updatePanel(panel, state) {
    panel.querySelectorAll("[data-sdc-option]").forEach((option) => {
      const key = option.getAttribute("data-sdc-option");
      const value = option.getAttribute("data-sdc-value");
      const isSelected = state[key] === value;

      option.classList.toggle("is-selected", isSelected);
      option.setAttribute("aria-pressed", isSelected ? "true" : "false");
    });

    panel.querySelectorAll("[data-sdc-output]").forEach((output) => {
      const env = [];
      const args = [];
      let command = output.getAttribute("data-sdc-base") || "";

      Object.entries(state).forEach(([key, value]) => {
        const selected = Array.from(
          panel.querySelectorAll(`[data-sdc-option="${key}"]`)
        ).find((option) => option.getAttribute("data-sdc-value") === value);

        if (!selected) {
          return;
        }

        const nextBase = selected.getAttribute("data-sdc-base");
        const nextEnv = selected.getAttribute("data-sdc-env");
        const nextArgs = selected.getAttribute("data-sdc-args");

        if (nextBase) {
          command = nextBase;
        }
        if (nextEnv) {
          env.push(nextEnv);
        }
        if (nextArgs) {
          args.push(nextArgs);
        }
      });

      const commandText = formatCommand(env, command, args, {
        indent: output.getAttribute("data-sdc-indent") || "  ",
        lineBreak: output.getAttribute("data-sdc-line-break") || "options",
      });
      output.textContent = commandText;
      if (!refreshHighlighting(output)) {
        highlightCommand(output);
      }
    });
  }

  function setupPanel(panel) {
    const state = readState(panel);

    panel.querySelectorAll("[data-sdc-option]").forEach((option) => {
      option.addEventListener("click", () => {
        state[option.getAttribute("data-sdc-option")] =
          option.getAttribute("data-sdc-value");
        updatePanel(panel, state);
      });
    });

    updatePanel(panel, state);
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-sdc]").forEach(setupPanel);
  });
})();
