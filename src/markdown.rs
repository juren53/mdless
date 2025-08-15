use pulldown_cmark::{Event, Parser, Tag, TagEnd};
use ratatui::style::{Color, Modifier, Style};
use ratatui::text::{Line, Span, Text};
use std::fs;
use std::path::Path;
use syntect::easy::HighlightLines;
use syntect::highlighting::{Style as SyntectStyle, ThemeSet};
use syntect::parsing::SyntaxSet;
use syntect::util::LinesWithEndings;

use crate::error::Result;

pub struct MarkdownRenderer {
    content: String,
    syntax_set: SyntaxSet,
    theme_set: ThemeSet,
}

impl MarkdownRenderer {
    pub fn new() -> Self {
        Self {
            content: String::new(),
            syntax_set: SyntaxSet::load_defaults_newlines(),
            theme_set: ThemeSet::load_defaults(),
        }
    }

    pub fn load_file<P: AsRef<Path>>(&mut self, path: P) -> Result<()> {
        self.content = fs::read_to_string(path)?;
        Ok(())
    }

    pub fn render_to_text(&self) -> Text<'static> {
        let parser = Parser::new(&self.content);
        let mut lines = Vec::new();
        let mut current_line = Vec::new();
        let mut in_code_block = false;
        let mut code_block_language = String::new();
        let mut code_block_content = String::new();
        let mut in_heading = false;
        let mut heading_level = 0;
        let mut in_emphasis = false;
        let mut in_strong = false;
        let mut last_was_empty_line = true; // Track if the last line was empty

        for event in parser {
            match event {
                Event::Start(tag) => {
                    match tag {
                        Tag::Heading { level, .. } => {
                            // If we have content in current_line or the last line wasn't empty,
                            // we need to add spacing before the heading
                            if !current_line.is_empty() {
                                lines.push(Line::from(current_line.clone()));
                                current_line.clear();
                            }

                            // Add blank line before heading if the last line wasn't already empty
                            if !last_was_empty_line && !lines.is_empty() {
                                lines.push(Line::from(""));
                            }

                            in_heading = true;
                            heading_level = level as u8;
                        }
                        Tag::CodeBlock(lang) => {
                            in_code_block = true;
                            code_block_language = match lang {
                                pulldown_cmark::CodeBlockKind::Indented => String::new(),
                                pulldown_cmark::CodeBlockKind::Fenced(lang_str) => {
                                    lang_str.to_string()
                                }
                            };
                            code_block_content.clear();
                            if !current_line.is_empty() {
                                lines.push(Line::from(current_line.clone()));
                                current_line.clear();
                            }
                            // Add a blank line before code block for spacing
                            if !last_was_empty_line {
                                lines.push(Line::from(""));
                            }
                        }
                        Tag::Emphasis => {
                            in_emphasis = true;
                        }
                        Tag::Strong => {
                            in_strong = true;
                        }
                        Tag::Paragraph => {
                            // Start new paragraph
                        }
                        _ => {}
                    }
                }
                Event::End(tag_end) => match tag_end {
                    TagEnd::Heading(_) => {
                        in_heading = false;
                        if !current_line.is_empty() {
                            lines.push(Line::from(current_line.clone()));
                            current_line.clear();
                        }
                        lines.push(Line::from(""));
                        last_was_empty_line = true;
                    }
                    TagEnd::CodeBlock => {
                        in_code_block = false;

                        // Render the collected code block with syntax highlighting
                        let highlighted_lines =
                            self.highlight_code_block(&code_block_content, &code_block_language);

                        // Add top border (79 characters wide)
                        lines.push(Line::from(vec![Span::styled(
                            "┌─────────────────────────────────────────────────────────────────────────────┐",
                            Style::default().fg(Color::DarkGray)
                        )]));

                        // Add language label if present
                        if !code_block_language.is_empty() {
                            // Calculate proper padding for language label
                            // The border is 79 display characters wide
                            // Content structure: "│ " + language + padding + "│"
                            // We want: 2 (for "│ ") + language_len + padding + 1 (for "│") = 79 chars
                            let language_display_width = code_block_language.chars().count();
                            let padding_needed =
                                79_usize.saturating_sub(2 + language_display_width + 1);

                            lines.push(Line::from(vec![
                                Span::styled("│ ", Style::default().fg(Color::DarkGray)),
                                Span::styled(
                                    code_block_language.clone(),
                                    Style::default()
                                        .fg(Color::Cyan)
                                        .add_modifier(Modifier::BOLD),
                                ),
                                Span::styled(" ".repeat(padding_needed), Style::default()),
                                Span::styled("│", Style::default().fg(Color::DarkGray)),
                            ]));
                            lines.push(Line::from(vec![Span::styled(
                                "├─────────────────────────────────────────────────────────────────────────────┤",
                                Style::default().fg(Color::DarkGray)
                            )]));
                        }

                        // Add highlighted code lines
                        for highlighted_line in highlighted_lines {
                            lines.push(highlighted_line);
                        }

                        // Add bottom border
                        lines.push(Line::from(vec![Span::styled(
                            "└─────────────────────────────────────────────────────────────────────────────┘",
                            Style::default().fg(Color::DarkGray)
                        )]));

                        lines.push(Line::from(""));
                        last_was_empty_line = true;
                        code_block_content.clear();
                        code_block_language.clear();
                    }
                    TagEnd::Emphasis => {
                        in_emphasis = false;
                    }
                    TagEnd::Strong => {
                        in_strong = false;
                    }
                    TagEnd::Paragraph => {
                        if !current_line.is_empty() {
                            lines.push(Line::from(current_line.clone()));
                            current_line.clear();
                        }
                        lines.push(Line::from(""));
                        last_was_empty_line = true;
                    }
                    _ => {}
                },
                Event::Text(text) => {
                    if in_code_block {
                        code_block_content.push_str(&text);
                    } else {
                        let style = self.get_text_style(
                            in_heading,
                            heading_level,
                            in_code_block,
                            in_emphasis,
                            in_strong,
                        );

                        current_line.push(Span::styled(text.to_string(), style));
                        // Text content means we're not on an empty line
                        if !text.trim().is_empty() {
                            last_was_empty_line = false;
                        }
                    }
                }
                Event::Code(code) => {
                    let style = Style::default()
                        .fg(Color::Yellow)
                        .bg(Color::Rgb(40, 40, 40))
                        .add_modifier(Modifier::BOLD);
                    current_line.push(Span::styled(format!(" {} ", code), style));
                    last_was_empty_line = false;
                }
                Event::SoftBreak | Event::HardBreak => {
                    if !current_line.is_empty() {
                        lines.push(Line::from(current_line.clone()));
                        current_line.clear();
                        last_was_empty_line = false;
                    }
                }
                _ => {}
            }
        }

        if !current_line.is_empty() {
            lines.push(Line::from(current_line));
        }

        Text::from(lines)
    }

    fn highlight_code_block(&self, code: &str, language: &str) -> Vec<Line<'static>> {
        let mut lines = Vec::new();

        // Try to find the syntax for the given language
        let syntax = if language.is_empty() {
            self.syntax_set.find_syntax_plain_text()
        } else {
            self.syntax_set
                .find_syntax_by_token(language)
                .or_else(|| self.syntax_set.find_syntax_by_extension(language))
                .unwrap_or_else(|| self.syntax_set.find_syntax_plain_text())
        };

        // Use a dark theme for better terminal compatibility
        let theme = &self.theme_set.themes["base16-ocean.dark"];
        let mut highlighter = HighlightLines::new(syntax, theme);

        for line in LinesWithEndings::from(code) {
            let highlighted = highlighter
                .highlight_line(line, &self.syntax_set)
                .unwrap_or_else(|_| vec![(SyntectStyle::default(), line)]);

            let mut spans = vec![Span::styled("│ ", Style::default().fg(Color::DarkGray))];

            for (style, text) in highlighted {
                let ratatui_style = self.syntect_style_to_ratatui(style);
                // Strip newlines from the text since they don't contribute to display width
                let display_text = text.trim_end_matches('\n');
                if !display_text.is_empty() {
                    spans.push(Span::styled(display_text.to_string(), ratatui_style));
                }
            }

            // Pad the line to fit within the border
            // Target: "│ " + content + padding + "│" = 79 display characters
            let content_length: usize = spans
                .iter()
                .skip(1)
                .map(|s| s.content.chars().count())
                .sum();
            let padding_needed = 79_usize.saturating_sub(2 + content_length + 1);
            spans.push(Span::styled(" ".repeat(padding_needed), Style::default()));

            spans.push(Span::styled("│", Style::default().fg(Color::DarkGray)));
            lines.push(Line::from(spans));
        }

        // If no lines were added (empty code block), add an empty line
        if lines.is_empty() {
            lines.push(Line::from(vec![
                Span::styled("│", Style::default().fg(Color::DarkGray)),
                Span::styled(" ".repeat(76), Style::default()), // 79 - 2 - 1 = 76 spaces
                Span::styled("│", Style::default().fg(Color::DarkGray)),
            ]));
        }

        lines
    }

    fn syntect_style_to_ratatui(&self, syntect_style: SyntectStyle) -> Style {
        let mut style = Style::default();

        // Convert foreground color
        let fg_color = syntect_style.foreground;
        style = style.fg(Color::Rgb(fg_color.r, fg_color.g, fg_color.b));

        // Convert background color if it's not transparent
        if syntect_style.background.a > 0 {
            let bg_color = syntect_style.background;
            style = style.bg(Color::Rgb(bg_color.r, bg_color.g, bg_color.b));
        } else {
            // Use a dark background for code blocks
            style = style.bg(Color::Rgb(30, 30, 30));
        }

        // Convert font style
        if syntect_style
            .font_style
            .contains(syntect::highlighting::FontStyle::BOLD)
        {
            style = style.add_modifier(Modifier::BOLD);
        }
        if syntect_style
            .font_style
            .contains(syntect::highlighting::FontStyle::ITALIC)
        {
            style = style.add_modifier(Modifier::ITALIC);
        }
        if syntect_style
            .font_style
            .contains(syntect::highlighting::FontStyle::UNDERLINE)
        {
            style = style.add_modifier(Modifier::UNDERLINED);
        }

        style
    }

    fn get_text_style(
        &self,
        in_heading: bool,
        heading_level: u8,
        in_code_block: bool,
        in_emphasis: bool,
        in_strong: bool,
    ) -> Style {
        let mut style = Style::default();

        if in_heading {
            style = match heading_level {
                1 => style.fg(Color::Red).add_modifier(Modifier::BOLD),
                2 => style.fg(Color::Yellow).add_modifier(Modifier::BOLD),
                3 => style.fg(Color::Green).add_modifier(Modifier::BOLD),
                4 => style.fg(Color::Cyan).add_modifier(Modifier::BOLD),
                5 => style.fg(Color::Blue).add_modifier(Modifier::BOLD),
                _ => style.fg(Color::Magenta).add_modifier(Modifier::BOLD),
            };
        }

        if in_code_block {
            style = style.fg(Color::Green).bg(Color::DarkGray);
        }

        if in_emphasis {
            style = style.add_modifier(Modifier::ITALIC);
        }

        if in_strong {
            style = style.add_modifier(Modifier::BOLD);
        }

        style
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_new_renderer() {
        let renderer = MarkdownRenderer::new();
        assert!(renderer.content.is_empty());
    }

    #[test]
    fn test_render_simple_text() {
        let mut renderer = MarkdownRenderer::new();
        renderer.content = "Hello, world!".to_string();

        let text = renderer.render_to_text();
        assert!(!text.lines.is_empty());
    }

    #[test]
    fn test_render_heading() {
        let mut renderer = MarkdownRenderer::new();
        renderer.content = "# Main Title\n\nSome content".to_string();

        let text = renderer.render_to_text();
        assert!(text.lines.len() >= 2);
    }

    #[test]
    fn test_header_spacing_fix() {
        let mut renderer = MarkdownRenderer::new();
        renderer.content =
            "Some paragraph text.\n### Header without spacing\nMore content.".to_string();

        let text = renderer.render_to_text();

        // The rendered text should have proper spacing before the header
        // We expect: paragraph line, empty line, header line, empty line, content line
        assert!(
            text.lines.len() >= 5,
            "Should have at least 5 lines with proper spacing"
        );

        // Check that there's an empty line before the header
        let lines_text: Vec<String> = text
            .lines
            .iter()
            .map(|line| {
                line.spans
                    .iter()
                    .map(|span| span.content.as_ref())
                    .collect::<String>()
            })
            .collect();

        // Find the header line
        let header_index = lines_text
            .iter()
            .position(|line| line.contains("Header without spacing"));
        assert!(header_index.is_some(), "Header should be found");

        let header_idx = header_index.unwrap();
        // There should be an empty line before the header (unless it's the first line)
        if header_idx > 0 {
            assert!(
                lines_text[header_idx - 1].trim().is_empty(),
                "There should be an empty line before the header"
            );
        }
    }

    #[test]
    fn test_multiple_headers_without_spacing() {
        let mut renderer = MarkdownRenderer::new();
        renderer.content =
            "Paragraph.\n### First Header\nContent.\n### Second Header\nMore content.".to_string();

        let text = renderer.render_to_text();

        // Should have proper spacing before both headers
        let lines_text: Vec<String> = text
            .lines
            .iter()
            .map(|line| {
                line.spans
                    .iter()
                    .map(|span| span.content.as_ref())
                    .collect::<String>()
            })
            .collect();

        let first_header_idx = lines_text
            .iter()
            .position(|line| line.contains("First Header"));
        let second_header_idx = lines_text
            .iter()
            .position(|line| line.contains("Second Header"));

        assert!(
            first_header_idx.is_some() && second_header_idx.is_some(),
            "Both headers should be found"
        );

        // Both headers should have empty lines before them
        if let Some(idx) = first_header_idx {
            if idx > 0 {
                assert!(
                    lines_text[idx - 1].trim().is_empty(),
                    "First header should have empty line before it"
                );
            }
        }

        if let Some(idx) = second_header_idx {
            if idx > 0 {
                assert!(
                    lines_text[idx - 1].trim().is_empty(),
                    "Second header should have empty line before it"
                );
            }
        }
    }

    #[test]
    fn test_code_block_border_alignment() {
        let mut renderer = MarkdownRenderer::new();
        renderer.content = "```rust\nfn main() {}\n```".to_string();

        let text = renderer.render_to_text();

        // Find the language header line (contains "rust")
        let language_line_idx = text
            .lines
            .iter()
            .position(|line| line.spans.iter().any(|span| span.content.contains("rust")))
            .expect("Should find language header line");

        let language_line = &text.lines[language_line_idx];

        // Calculate the display width (character count, not byte count)
        let display_width: usize = language_line
            .spans
            .iter()
            .map(|s| s.content.chars().count())
            .sum();

        // The language header line should have exactly 79 display characters to match the border
        assert_eq!(
            display_width, 79,
            "Language line should be exactly 79 display characters wide"
        );

        // Check that it has the proper structure
        assert!(
            language_line.spans.len() >= 3,
            "Should have at least 3 spans"
        );
        assert_eq!(
            language_line.spans[0].content.chars().count(),
            2,
            "First span should be '│ ' (2 chars)"
        );
        assert_eq!(
            language_line.spans.last().unwrap().content.chars().count(),
            1,
            "Last span should be '│' (1 char)"
        );
    }

    #[test]
    fn test_code_block_content_line_alignment() {
        let mut renderer = MarkdownRenderer::new();
        renderer.content = "```rust\nfn main() {\n    println!(\"Hello, world!\");\n}\n```".to_string();

        let text = renderer.render_to_text();

        // Find all lines that contain code content (between borders)
        let code_content_lines: Vec<&Line> = text
            .lines
            .iter()
            .filter(|line| {
                // Code content lines start with "│ " and end with "│"
                line.spans.len() >= 2
                    && line.spans[0].content == "│ "
                    && line.spans.last().unwrap().content == "│"
                    && !line.spans.iter().any(|span| span.content.contains("─")) // Not a border line
                    && !line.spans.iter().any(|span| span.content.contains("rust")) // Not the language line
            })
            .collect();

        // Each code content line should have exactly 79 display characters
        for line in code_content_lines {
            let display_width: usize = line
                .spans
                .iter()
                .map(|s| s.content.chars().count())
                .sum();

            assert_eq!(
                display_width, 79,
                "Code content line should be exactly 79 display characters wide"
            );
        }
    }
}
