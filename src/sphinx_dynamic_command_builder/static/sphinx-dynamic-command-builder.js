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

  function shellQuote(value) {
    if (value === "") {
      return '""';
    }
    if (/^[A-Za-z0-9_@%+=:,./-]+$/.test(value)) {
      return value;
    }
    return `'${value.replace(/'/g, "'\"'\"'")}'`;
  }

  function replaceInputPlaceholders(text, state) {
    return text.replace(/\{([A-Za-z0-9_-]+)\}/g, (placeholder, key) => {
      if (!Object.prototype.hasOwnProperty.call(state.inputs, key)) {
        return placeholder;
      }
      return shellQuote(state.inputs[key]);
    });
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

  function getOptionKey(option) {
    return option.getAttribute("data-sdc-option");
  }

  function getOptionValue(option) {
    return option.getAttribute("data-sdc-value");
  }

  function getOptions(panel, key) {
    return Array.from(panel.querySelectorAll("[data-sdc-option]")).filter(
      (option) => getOptionKey(option) === key
    );
  }

  function isMultipleOption(option) {
    return option.getAttribute("data-sdc-multiple") === "true";
  }

  function isMultipleGroup(options) {
    return options.some(isMultipleOption);
  }

  function selectedValues(value) {
    return Array.isArray(value) ? value : [value];
  }

  function selectedOptions(panel, key, value) {
    const values = selectedValues(value);
    return getOptions(panel, key).filter((option) =>
      values.includes(getOptionValue(option))
    );
  }

  function readState(panel) {
    const keys = Array.from(
      new Set(
        Array.from(panel.querySelectorAll("[data-sdc-option]")).map((option) =>
          getOptionKey(option)
        )
      )
    );

    const inputState = Array.from(panel.querySelectorAll("[data-sdc-input]")).reduce(
      (state, input) => {
        state[input.getAttribute("data-sdc-input")] = input.value;
        return state;
      },
      {}
    );

    return keys.reduce((state, key) => {
      const options = getOptions(panel, key);
      const defaults = options.filter(
        (option) => option.getAttribute("data-sdc-default") === "true"
      );

      if (isMultipleGroup(options)) {
        state[key] = defaults.map(getOptionValue);
        return state;
      }

      const selected = defaults[0];
      const first = options[0];
      state[key] = (selected || first)?.getAttribute("data-sdc-value") || "";
      return state;
    }, { inputs: inputState });
  }

  function updatePanel(panel, state) {
    panel.querySelectorAll("[data-sdc-option]").forEach((option) => {
      const key = getOptionKey(option);
      const value = getOptionValue(option);
      const isSelected = selectedValues(state[key]).includes(value);

      option.classList.toggle("is-selected", isSelected);
      option.setAttribute("aria-pressed", isSelected ? "true" : "false");
    });

    panel.querySelectorAll("[data-sdc-output]").forEach((output) => {
      const env = [];
      const args = [];
      let command = replaceInputPlaceholders(
        output.getAttribute("data-sdc-base") || "",
        state
      );

      Object.entries(state).forEach(([key, value]) => {
        if (key === "inputs") {
          return;
        }
        selectedOptions(panel, key, value).forEach((selected) => {
          const nextBase = selected.getAttribute("data-sdc-base");
          const nextEnv = selected.getAttribute("data-sdc-env");
          const nextArgs = selected.getAttribute("data-sdc-args");

          if (nextBase) {
            command = replaceInputPlaceholders(nextBase, state);
          }
          if (nextEnv) {
            env.push(replaceInputPlaceholders(nextEnv, state));
          }
          if (nextArgs) {
            args.push(replaceInputPlaceholders(nextArgs, state));
          }
        });
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

    panel.querySelectorAll("[data-sdc-input]").forEach((input) => {
      input.addEventListener("input", () => {
        state.inputs[input.getAttribute("data-sdc-input")] = input.value;
        updatePanel(panel, state);
      });
    });

    panel.querySelectorAll("[data-sdc-option]").forEach((option) => {
      option.addEventListener("click", () => {
        const key = getOptionKey(option);
        const value = getOptionValue(option);

        if (isMultipleOption(option)) {
          const values = Array.isArray(state[key]) ? state[key] : [];
          state[key] = values.includes(value)
            ? values.filter((selectedValue) => selectedValue !== value)
            : [...values, value];
        } else {
          state[key] = value;
        }
        updatePanel(panel, state);
      });
    });

    updatePanel(panel, state);
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-sdc]").forEach(setupPanel);
  });
})();
