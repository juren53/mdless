use thiserror::Error;

#[derive(Debug, Error)]
pub enum MdViewError {
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),

    #[error("File watch error: {0}")]
    FileWatch(#[from] notify::Error),

    #[error("Terminal error: {0}")]
    Terminal(String),
}

pub type Result<T> = std::result::Result<T, MdViewError>;
