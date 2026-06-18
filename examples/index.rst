sphinx-dynamic-command-builder example
======================================

This page is built by Sphinx and renders the command builder through the
``sphinx_dynamic_command_builder`` extension.

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
     - label: Extras
       key: extras
       multiple: true
       default:
         - heading
       choices:
         - label: Line numbers
           value: line_numbers
           args: --line-number
         - label: Headings
           value: heading
           args: --heading
         - label: JSON
           value: json
           args: --json
