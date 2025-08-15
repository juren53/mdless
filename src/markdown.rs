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

        for event in parser {
            match event {
                Event::Start(tag) => {
                    match tag {
                        Tag::Heading { level, .. } => {
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
                    }
                    TagEnd::CodeBlock => {
                        in_code_block = false;
                        lines.push(Line::from(""));
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
                        }
                    } else {
                        current_line.push(Span::styled(text.to_string(), style));
                    }
                }
                Event::Code(code) => {
                    let style = Style::default().fg(Color::Yellow).bg(Color::DarkGray);
                    current_line.push(Span::styled(format!("`{}`", code), style));
                }
                Event::SoftBreak | Event::HardBreak => {
                    if !current_line.is_empty() {
                        lines.push(Line::from(current_line.clone()));
                        current_line.clear();
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
    fn test_render_code_block() {
        let mut renderer = MarkdownRenderer::new();
        renderer.content = "```rust\nfn main() {}\n```".to_string();
        
        let text = renderer.render_to_text();
        assert!(!text.lines.is_empty());
    }
}
