use anyhow::Result;
use clap::Parser;
use std::path::PathBuf;

mod app;
mod error;
mod markdown;
mod ui;

use app::App;

#[derive(Parser)]
#[command(name = "mdview")]
#[command(about = "A terminal-based markdown file viewer")]
#[command(version)]
struct Cli {
    /// Path to the markdown file to view
    file: PathBuf,

    /// Enable file watching for live updates
    #[arg(short, long)]
    watch: bool,
}

fn main() -> Result<()> {
    let cli = Cli::parse();

    if !cli.file.exists() {
        anyhow::bail!("File does not exist: {}", cli.file.display());
    }

    if !cli.file.is_file() {
        anyhow::bail!("Path is not a file: {}", cli.file.display());
    }

    let mut app = App::new(cli.file, cli.watch)?;
    app.run()?;

    Ok(())
}
