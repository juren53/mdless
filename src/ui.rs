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

use ratatui::{
    Frame,
    layout::{Constraint, Direction, Layout, Rect},
    style::{Color, Style},
    text::{Line, Span},
    widgets::{Block, Borders, Paragraph, Scrollbar, ScrollbarOrientation, ScrollbarState},
};

use crate::app::App;

pub fn draw(frame: &mut Frame, app: &mut App) {
    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(3), // Header
            Constraint::Min(0),    // Content
            Constraint::Length(3), // Footer
        ])
        .split(frame.area());

    draw_header(frame, chunks[0], app);
    draw_content(frame, chunks[1], app);
    draw_footer(frame, chunks[2], app);
}

fn draw_header(frame: &mut Frame, area: Rect, app: &App) {
    let title = format!("mdless - {}", app.get_file_name());
    let header = Paragraph::new(title)
        .block(
            Block::default()
                .borders(Borders::ALL)
                .title("Markdown Viewer")
                .title_style(Style::default().fg(Color::Cyan)),
        )
        .style(Style::default().fg(Color::White));

    frame.render_widget(header, area);
}

fn draw_content(frame: &mut Frame, area: Rect, app: &mut App) {
    let content = app.get_rendered_content().clone();

    let paragraph = Paragraph::new(content)
        .block(Block::default().borders(Borders::ALL))
        .scroll((app.get_scroll_offset(), 0))
        .wrap(ratatui::widgets::Wrap { trim: true });

    frame.render_widget(paragraph, area);

    // Render scrollbar
    let scrollbar = Scrollbar::default()
        .orientation(ScrollbarOrientation::VerticalRight)
        .begin_symbol(Some("↑"))
        .end_symbol(Some("↓"));

    let mut scrollbar_state = ScrollbarState::default()
        .content_length(app.get_content_length() as usize)
        .position(app.get_scroll_offset() as usize);

    frame.render_stateful_widget(
        scrollbar,
        area.inner(ratatui::layout::Margin {
            vertical: 1,
            horizontal: 0,
        }),
        &mut scrollbar_state,
    );
}

fn draw_footer(frame: &mut Frame, area: Rect, app: &App) {
    let help_text = if app.is_watching() {
        "Press 'q' to quit | ↑/↓ or j/k to scroll | Watching for file changes..."
    } else {
        "Press 'q' to quit | ↑/↓ or j/k to scroll | 'r' to reload"
    };

    let footer = Paragraph::new(Line::from(vec![Span::styled(
        help_text,
        Style::default().fg(Color::Gray),
    )]))
    .block(
        Block::default()
            .borders(Borders::ALL)
            .title("Help")
            .title_style(Style::default().fg(Color::Green)),
    );

    frame.render_widget(footer, area);
}
