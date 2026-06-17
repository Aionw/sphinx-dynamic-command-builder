(() => {
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

      output.textContent = [...env, command, ...args].filter(Boolean).join(" ");
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

