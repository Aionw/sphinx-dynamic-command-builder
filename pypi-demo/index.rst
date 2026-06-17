PyPI demo for sphinx-dynamic-command-builder
=============================================

This page is intentionally built from the PyPI package installation, not from
the local ``src`` tree.

.. dynamic-command::

   base: rg dynamic-command .
   command_label: Search command
   format:
     line_break: options
     indent: "  "
   options:
     - label: Match mode
       key: match_mode
       default: smart
       choices:
         - label: Smart case
           value: smart
           args: --smart-case
         - label: Case sensitive
           value: sensitive
         - label: Ignore case
           value: ignore
           args: --ignore-case
     - label: Context
       key: context
       default: none
       choices:
         - label: None
           value: none
         - label: 2 lines
           value: two
           args: --context 2
         - label: 5 lines
           value: five
           args: --context 5
     - label: Files
       key: files
       default: normal
       choices:
         - label: Respect ignore files
           value: normal
         - label: Include hidden
           value: hidden
           args: --hidden
         - label: Include ignored
           value: ignored
           args: --hidden --no-ignore
     - label: Type filter
       key: type
       default: all
       choices:
         - label: All files
           value: all
         - label: Python
           value: python
           args: --type py
         - label: Markdown
           value: markdown
           args: --type md
