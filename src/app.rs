// Copyright 2025 Ray Krueger <raykrueger@gmail.com>
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

use crossterm::{
    event::{self, DisableMouseCapture, EnableMouseCapture, Event, KeyCode, KeyEventKind},
    execute,
    terminal::{EnterAlternateScreen, LeaveAlternateScreen, disable_raw_mode, enable_raw_mode},
};
use notify::{RecommendedWatcher, RecursiveMode, Watcher};
use ratatui::{
    Terminal,
    backend::{Backend, CrosstermBackend},
    text::Text,
};
use std::{io, path::PathBuf, sync::mpsc, time::Duration};

use crate::error::{MdViewError, Result};
use crate::markdown::MarkdownRenderer;
use crate::ui;

pub struct App {
    file_path: PathBuf,
    renderer: MarkdownRenderer,
    rendered_content: Text<'static>,
    scroll_offset: u16,
    content_length: u16,
    watching: bool,
    should_quit: bool,
    #[allow(dead_code)]
    file_watcher: Option<RecommendedWatcher>,
    file_change_rx: Option<mpsc::Receiver<()>>,
}

impl App {
    pub fn new(file_path: PathBuf, watch: bool) -> Result<Self> {
        let mut renderer = MarkdownRenderer::new();
        renderer.load_file(&file_path)?;
        let rendered_content = renderer.render_to_text();
        let content_length = rendered_content.lines.len() as u16;

        let (file_watcher, file_change_rx) = if watch {
            let (tx, rx) = mpsc::channel();
            let mut watcher = notify::recommended_watcher(move |_| {
                let _ = tx.send(());
            })?;

            watcher.watch(&file_path, RecursiveMode::NonRecursive)?;
            (Some(watcher), Some(rx))
        } else {
            (None, None)
        };

        Ok(Self {
            file_path,
            renderer,
            rendered_content,
            scroll_offset: 0,
            content_length,
            watching: watch,
            should_quit: false,
            file_watcher,
            file_change_rx,
        })
    }

    pub fn run(&mut self) -> Result<()> {
        // Setup terminal
        enable_raw_mode().map_err(|e| MdViewError::Terminal(e.to_string()))?;
        let mut stdout = io::stdout();
        execute!(stdout, EnterAlternateScreen, EnableMouseCapture)
            .map_err(|e| MdViewError::Terminal(e.to_string()))?;
        let backend = CrosstermBackend::new(stdout);
        let mut terminal =
            Terminal::new(backend).map_err(|e| MdViewError::Terminal(e.to_string()))?;

        let result = self.run_app(&mut terminal);

        // Restore terminal
        disable_raw_mode().map_err(|e| MdViewError::Terminal(e.to_string()))?;
        execute!(
            terminal.backend_mut(),
            LeaveAlternateScreen,
            DisableMouseCapture
        )
        .map_err(|e| MdViewError::Terminal(e.to_string()))?;
        terminal
            .show_cursor()
            .map_err(|e| MdViewError::Terminal(e.to_string()))?;

        result
    }

    fn run_app<B: Backend>(&mut self, terminal: &mut Terminal<B>) -> Result<()> {
        loop {
            terminal
                .draw(|f| ui::draw(f, self))
                .map_err(|e| MdViewError::Terminal(e.to_string()))?;

            if self.should_quit {
                break;
            }

            // Check for file changes if watching
            if let Some(ref rx) = self.file_change_rx
                && rx.try_recv().is_ok()
            {
                self.reload_file()?;
            }

            // Handle input events
            if event::poll(Duration::from_millis(100))
                .map_err(|e| MdViewError::Terminal(e.to_string()))?
                && let Event::Key(key) =
                    event::read().map_err(|e| MdViewError::Terminal(e.to_string()))?
                && key.kind == KeyEventKind::Press
            {
                self.handle_key_event(key.code);
            }
        }

        Ok(())
    }

    fn handle_key_event(&mut self, key_code: KeyCode) {
        match key_code {
            // Quit
            KeyCode::Char('q') => {
                self.should_quit = true;
            }
            // Reload file
            KeyCode::Char('r') => {
                if let Err(e) = self.reload_file() {
                    eprintln!("Failed to reload file: {}", e);
                }
            }
            // Vim-style movement: up
            KeyCode::Up | KeyCode::Char('k') => {
                self.scroll_up();
            }
            // Vim-style movement: down
            KeyCode::Down | KeyCode::Char('j') => {
                self.scroll_down();
            }
            // Vim-style movement: half page up
            KeyCode::Char('u') => {
                self.scroll_half_page_up();
            }
            // Vim-style movement: half page down
            KeyCode::Char('d') => {
                self.scroll_half_page_down();
            }
            // Vim-style movement: full page up
            KeyCode::PageUp | KeyCode::Char('b') => {
                self.scroll_page_up();
            }
            // Vim-style movement: full page down
            KeyCode::PageDown | KeyCode::Char('f') => {
                self.scroll_page_down();
            }
            // Vim-style movement: top of document
            KeyCode::Home | KeyCode::Char('g') => {
                self.scroll_to_top();
            }
            // Vim-style movement: bottom of document
            KeyCode::End | KeyCode::Char('G') => {
                self.scroll_to_bottom();
            }
            // Vim-style movement: move up 5 lines
            KeyCode::Char('K') => {
                for _ in 0..5 {
                    self.scroll_up();
                }
            }
            // Vim-style movement: move down 5 lines
            KeyCode::Char('J') => {
                for _ in 0..5 {
                    self.scroll_down();
                }
            }
            // Vim-style movement: move to middle of screen
            KeyCode::Char('M') => {
                self.scroll_to_middle();
            }
            // Vim-style movement: move up 10 lines (alternative to page up)
            KeyCode::Char('U') => {
                for _ in 0..10 {
                    self.scroll_up();
                }
            }
            // Vim-style movement: move down 10 lines (alternative to page down)
            KeyCode::Char('D') => {
                for _ in 0..10 {
                    self.scroll_down();
                }
            }
            _ => {}
        }
    }

    fn scroll_up(&mut self) {
        self.scroll_offset = self.scroll_offset.saturating_sub(1);
    }

    fn scroll_down(&mut self) {
        if self.scroll_offset < self.content_length.saturating_sub(1) {
            self.scroll_offset += 1;
        }
    }

    fn scroll_half_page_up(&mut self) {
        let half_page = 10; // Could be made configurable based on terminal height
        self.scroll_offset = self.scroll_offset.saturating_sub(half_page);
    }

    fn scroll_half_page_down(&mut self) {
        let half_page = 10; // Could be made configurable based on terminal height
        let new_offset = self.scroll_offset.saturating_add(half_page);
        self.scroll_offset = new_offset.min(self.content_length.saturating_sub(1));
    }

    fn scroll_page_up(&mut self) {
        let full_page = 20; // Could be made configurable based on terminal height
        self.scroll_offset = self.scroll_offset.saturating_sub(full_page);
    }

    fn scroll_page_down(&mut self) {
        let full_page = 20; // Could be made configurable based on terminal height
        let new_offset = self.scroll_offset.saturating_add(full_page);
        self.scroll_offset = new_offset.min(self.content_length.saturating_sub(1));
    }

    fn scroll_to_top(&mut self) {
        self.scroll_offset = 0;
    }

    fn scroll_to_bottom(&mut self) {
        self.scroll_offset = self.content_length.saturating_sub(1);
    }

    fn scroll_to_middle(&mut self) {
        self.scroll_offset = self.content_length / 2;
    }

    fn reload_file(&mut self) -> Result<()> {
        self.renderer.load_file(&self.file_path)?;
        self.rendered_content = self.renderer.render_to_text();
        self.content_length = self.rendered_content.lines.len() as u16;

        // Adjust scroll offset if content is shorter
        if self.scroll_offset >= self.content_length {
            self.scroll_offset = self.content_length.saturating_sub(1);
        }

        Ok(())
    }

    pub fn get_file_name(&self) -> String {
        self.file_path
            .file_name()
            .and_then(|name| name.to_str())
            .unwrap_or("Unknown")
            .to_string()
    }

    pub fn get_rendered_content(&self) -> &Text<'static> {
        &self.rendered_content
    }

    pub fn get_scroll_offset(&self) -> u16 {
        self.scroll_offset
    }

    pub fn get_content_length(&self) -> u16 {
        self.content_length
    }

    pub fn is_watching(&self) -> bool {
        self.watching
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use tempfile::NamedTempFile;

    fn create_test_app() -> App {
        let temp_file = NamedTempFile::new().unwrap();
        fs::write(&temp_file, "# Test\n\nLine 1\nLine 2\nLine 3\nLine 4\nLine 5\nLine 6\nLine 7\nLine 8\nLine 9\nLine 10\nLine 11\nLine 12\nLine 13\nLine 14\nLine 15\nLine 16\nLine 17\nLine 18\nLine 19\nLine 20").unwrap();

        App::new(temp_file.path().to_path_buf(), false).unwrap()
    }

    #[test]
    fn test_scroll_to_top() {
        let mut app = create_test_app();
        app.scroll_offset = 10;
        app.scroll_to_top();
        assert_eq!(app.scroll_offset, 0);
    }

    #[test]
    fn test_scroll_to_bottom() {
        let mut app = create_test_app();
        app.scroll_to_bottom();
        assert_eq!(app.scroll_offset, app.content_length.saturating_sub(1));
    }

    #[test]
    fn test_scroll_to_middle() {
        let mut app = create_test_app();
        app.scroll_to_middle();
        assert_eq!(app.scroll_offset, app.content_length / 2);
    }

    #[test]
    fn test_scroll_half_page_up() {
        let mut app = create_test_app();
        app.scroll_offset = 15;
        app.scroll_half_page_up();
        assert_eq!(app.scroll_offset, 5);
    }

    #[test]
    fn test_scroll_half_page_down() {
        let mut app = create_test_app();
        app.scroll_offset = 5;
        app.scroll_half_page_down();
        assert_eq!(app.scroll_offset, 15);
    }

    #[test]
    fn test_scroll_bounds() {
        let mut app = create_test_app();

        // Test scrolling up from top
        app.scroll_offset = 0;
        app.scroll_up();
        assert_eq!(app.scroll_offset, 0);

        // Test scrolling down past bottom
        app.scroll_offset = app.content_length.saturating_sub(1);
        app.scroll_down();
        assert_eq!(app.scroll_offset, app.content_length.saturating_sub(1));
    }
}
