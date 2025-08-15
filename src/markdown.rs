use pulldown_cmark::{Event, Parser, Tag, TagEnd};
use ratatui::style::{Color, Modifier, Style};
use ratatui::text::{Line, Span, Text};
use std::fs;
use std::path::Path;

use crate::error::Result;

pub struct MarkdownRenderer {
    content: String,
}

impl MarkdownRenderer {
    pub fn new() -> Self {
        Self {
            content: String::new(),
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
                        Tag::CodeBlock(_) => {
                            in_code_block = true;
                            if !current_line.is_empty() {
                                lines.push(Line::from(current_line.clone()));
                                current_line.clear();
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
                        lines.push(Line::from(""));
                        last_was_empty_line = true;
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
                    let style = self.get_text_style(
                        in_heading,
                        heading_level,
                        in_code_block,
                        in_emphasis,
                        in_strong,
                    );

                    if in_code_block {
                        for line in text.lines() {
                            lines
                                .push(Line::from(vec![Span::styled(format!("  {}", line), style)]));
                            last_was_empty_line = line.trim().is_empty();
                        }
                    } else {
                        current_line.push(Span::styled(text.to_string(), style));
                        // Text content means we're not on an empty line
                        if !text.trim().is_empty() {
                            last_was_empty_line = false;
                        }
                    }
                }
                Event::Code(code) => {
                    let style = Style::default().fg(Color::Yellow).bg(Color::DarkGray);
                    current_line.push(Span::styled(format!("`{}`", code), style));
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
}
