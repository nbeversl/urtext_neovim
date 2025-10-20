# Urtext for Neovim

An implementation of Urtext in [Neovim](https://neovim.io/)

This is an early release for testers. Contributions are welcome.

## What is Urtext?

Urtext /ˈʊrtekst/ is a markup language for Python scriptable-notebooks in a text editor

For a fast overview, visit https://urtext.co/

## Installation

### Install urtext using pip.

`pip install urtext`
or
`pip3 install urtext` 

### Install the Neovim plugin

### with lazy.nvim
`{ "nbeversl/urtext_neovim" }`

### with packer.nvim
`use "nbeversl/urtext_neovim"`

### with vim-plug
`Plug 'nbeversl/urtext_neovim'`

## Starter Project & Documentation

Urtext can generate a starter project that documents its features with examples:

- Create and navigate to a folder for new the starter project
- Open Neovim from the new folder and type, `:UrtextStarterProject`  
- Type `<leader>zh` to open to the home node of the starter project.
- Read the home node to get started.

See https://urtext.co/documentation/ for more information.

## Other Implementations

There is also an implementation for:
- iOS using [Pythonista](https://omz-software.com/pythonista/), [urtext_pythonista](https://github.com/nbeversl/urtext_pythonista)
- a [plugin for Sublime Text](https://github.com/nbeversl/UrtextSublime)

## Questions and Issues

Questions and issues may be submitted either to https://urtext.co/support/ or to https://github.com/nbeversl/UrtextSublime/issues.
