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
      [...env, commandParts.prefix].filter(Boolean).join(" "),
      ...commandParts.options,
      ...args.flatMap((arg) => groupOptionTokens(tokenizeCommand(arg))),
    ].filter(Boolean);

    return lines
      .map((line, index) => {
        const continuation = index < lines.length - 1 ? " \\" : "";
        const indent = index === 0 ? "" : config.indent;
        return `${indent}${line}${continuation}`;
      })
      .join("\n");
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

      output.textContent = formatCommand(env, command, args, {
        indent: output.getAttribute("data-sdc-indent") || "  ",
        lineBreak: output.getAttribute("data-sdc-line-break") || "options",
      });
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
