# Available Colors for mdless-py

This document lists all available color options that can be used in your `config.yaml` file.

## Basic Colors

- `black`
- `red`
- `green`
- `yellow`
- `blue`
- `magenta`
- `cyan`
- `white`

## Bright Colors

- `bright_black` (gray)
- `bright_red`
- `bright_green`
- `bright_yellow`
- `bright_blue`
- `bright_magenta`
- `bright_cyan`
- `bright_white`

## Text Styles

- `bold`
- `italic`
- `underline`

## Configuration Elements

You can apply these colors to the following elements in your `config.yaml`:

### Colors Section

```yaml
colors:
  heading1: bright_red      # Level 1 headings (#)
  heading2: bright_red      # Level 2 headings (##)
  heading3: cyan            # Level 3 headings (###)
  heading4: cyan            # Level 4 headings (####)
  heading5: cyan            # Level 5 headings (#####)
  heading6: cyan            # Level 6 headings (######)
  code: yellow              # Inline code (`code`)
  code_block: yellow        # Code blocks (```code```)
  link: bright_cyan         # Links
  emphasis: italic          # Emphasized text (*text* or _text_)
  strong: bold              # Strong text (**text** or __text__)
  list_marker: green        # List bullets/numbers
  quote: magenta            # Block quotes (> quote)
  table_border: white       # Table borders
  footnote: bright_black    # Footnotes
```

## Example Configurations

### High Contrast (Light Backgrounds)
```yaml
colors:
  heading1: blue
  heading2: blue
  heading3: cyan
  code: magenta
  link: bright_blue
```

### Dark Theme (Dark Backgrounds)
```yaml
colors:
  heading1: bright_red
  heading2: bright_red
  heading3: bright_cyan
  code: bright_yellow
  link: bright_cyan
```

## Notes

- Not all terminal emulators support all colors equally
- Bright colors generally work better on dark backgrounds
- Basic colors generally work better on light backgrounds
- Text styles (bold, italic, underline) may not be supported in all terminals
- On Windows, make sure you're using a modern terminal like Windows Terminal for best color support
