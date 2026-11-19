use crate::config::EngineConfig;
use std::process::Stdio;
use tokio::process::Command;

pub struct PythonBridge {
    config: EngineConfig,
}

impl PythonBridge {
    pub fn new(config: EngineConfig) -> Self {
        Self { config }
    }

    /// Dispatches a sub-command to the companion Python studio.py
    pub async fn dispatch_studio(&self, args: &[&str]) -> Result<String, String> {
        let studio_py = self.config.studio_script();
        println!("🌉 [Rust IPC Bridge] Invoking Python Engine: {:?} with args {:?}", studio_py, args);

        let python_bin = if cfg!(target_os = "windows") { "python" } else { "python3" };

        let mut cmd = Command::new(python_bin);
        cmd.arg(&studio_py);
        for a in args {
            cmd.arg(a);
        }
        cmd.current_dir(&self.config.python_engine_dir);
        cmd.stdout(Stdio::piped());
        cmd.stderr(Stdio::piped());

        match cmd.output().await {
            Ok(output) => {
                let stdout = String::from_utf8_lossy(&output.stdout).to_string();
                let stderr = String::from_utf8_lossy(&output.stderr).to_string();
                if output.status.success() {
                    Ok(stdout)
                } else {
                    Err(format!("Python Engine Error:\n{}\n{}", stdout, stderr))
                }
            }
            Err(e) => Err(format!("Failed to spawn Python interpreter: {}", e)),
        }
    }

    /// Spawns a background job without blocking the Rust async event loop
    pub fn spawn_background_studio(&self, args: &[&str]) {
        let studio_py = self.config.studio_script();
        let python_bin = if cfg!(target_os = "windows") { "python" } else { "python3" };

        let mut cmd = std::process::Command::new(python_bin);
        cmd.arg(&studio_py);
        for a in args {
            cmd.arg(a);
        }
        cmd.current_dir(&self.config.python_engine_dir);
        let _ = cmd.spawn();
    }
}
