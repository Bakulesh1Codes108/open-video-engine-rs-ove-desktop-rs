use std::path::{Path, PathBuf};

#[derive(Debug, Clone)]
pub struct EngineConfig {
    pub python_engine_dir: PathBuf,
    pub ffmpeg_path: Option<PathBuf>,
    pub port: u16,
}

impl EngineConfig {
    pub fn detect(port: u16) -> Self {
        let mut candidates = vec![
            PathBuf::from("."),
            PathBuf::from("../Complete-Local-Video-Studio-Engine-"),
            PathBuf::from("../antigravity-video-studio"),
            PathBuf::from("Complete-Local-Video-Studio-Engine-"),
        ];

        let mut python_engine_dir = PathBuf::from(".");
        for cand in candidates {
            if cand.join("scripts/studio.py").exists() || cand.join("timeline.json").exists() {
                python_engine_dir = cand;
                break;
            }
        }

        let ffmpeg_path = which::which("ffmpeg").ok();

        Self {
            python_engine_dir,
            ffmpeg_path,
            port,
        }
    }

    pub fn studio_script(&self) -> PathBuf {
        self.python_engine_dir.join("scripts/studio.py")
    }

    pub fn timeline_file(&self) -> PathBuf {
        self.python_engine_dir.join("timeline.json")
    }
}

// Minimal fallback which check without external crate
mod which {
    use std::path::PathBuf;

    pub fn which(binary_name: &str) -> Result<PathBuf, ()> {
        if let Ok(path_var) = std::env::var("PATH") {
            for dir in std::env::split_paths(&path_var) {
                let candidate = dir.join(binary_name);
                if candidate.is_file() {
                    return Ok(candidate);
                }
                #[cfg(target_os = "windows")]
                {
                    let candidate_exe = dir.join(format!("{}.exe", binary_name));
                    if candidate_exe.is_file() {
                        return Ok(candidate_exe);
                    }
                }
            }
        }
        Err(())
    }
}
