use crossterm::{
    event::{self, DisableMouseCapture, EnableMouseCapture, Event, KeyCode, KeyEventKind},
    execute,
    terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen},
};
use notify::{RecommendedWatcher, RecursiveMode, Watcher};
use ratatui::{
    backend::{Backend, CrosstermBackend},
    text::Text,
    Terminal,
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
            if let Some(ref rx) = self.file_change_rx {
                if rx.try_recv().is_ok() {
                    self.reload_file()?;
                }
            }

            // Handle input events
            if event::poll(Duration::from_millis(100))
                .map_err(|e| MdViewError::Terminal(e.to_string()))?
            {
                if let Event::Key(key) =
                    event::read().map_err(|e| MdViewError::Terminal(e.to_string()))?
                {
                    if key.kind == KeyEventKind::Press {
                        self.handle_key_event(key.code);
                    }
                }
            }
        }

        Ok(())
    }

    fn handle_key_event(&mut self, key_code: KeyCode) {
        match key_code {
            KeyCode::Char('q') => {
                self.should_quit = true;
            }
            KeyCode::Char('r') => {
                if let Err(e) = self.reload_file() {
                    eprintln!("Failed to reload file: {}", e);
                }
            }
            KeyCode::Up | KeyCode::Char('k') => {
                self.scroll_up();
            }
            KeyCode::Down | KeyCode::Char('j') => {
                self.scroll_down();
            }
            KeyCode::PageUp => {
                for _ in 0..10 {
                    self.scroll_up();
                }
            }
            KeyCode::PageDown => {
                for _ in 0..10 {
                    self.scroll_down();
                }
            }
            KeyCode::Home => {
                self.scroll_offset = 0;
            }
            KeyCode::End => {
                self.scroll_offset = self.content_length.saturating_sub(1);
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
