use std::path::Path;
use tokio::fs;
use tokio::process::Command;

pub struct NativeFfmpeg;

impl NativeFfmpeg {
    /// Losslessly merges multiple MP4 files using FFmpeg's concat demuxer (0 re-encoding).
    pub async fn concat_videos(input_files: &[String], output_path: &str) -> Result<String, String> {
        if input_files.is_empty() {
            return Err("No input files provided for concatenation.".to_string());
        }

        let manifest_path = "out/_rust_concat_manifest.txt";
        if let Some(parent) = Path::new(manifest_path).parent() {
            let _ = fs::create_dir_all(parent).await;
        }

        let mut manifest_content = String::new();
        for file in input_files {
            if Path::new(file).exists() {
                let canonical = fs::canonicalize(file)
                    .await
                    .map_err(|e| format!("Failed to resolve path {}: {}", file, e))?;
                manifest_content.push_str(&format!("file '{}'\n", canonical.to_string_lossy().replace('\\', "/")));
            }
        }

        fs::write(manifest_path, manifest_content)
            .await
            .map_err(|e| format!("Failed to write concat manifest: {}", e))?;

        println!("🦀 [Rust FFmpeg] Native Lossless Concat merging {} clips into {}", input_files.len(), output_path);

        let output = Command::new("ffmpeg")
            .arg("-y")
            .arg("-f")
            .arg("concat")
            .arg("-safe")
            .arg("0")
            .arg("-i")
            .arg(manifest_path)
            .arg("-c")
            .arg("copy")
            .arg(output_path)
            .output()
            .await;

        let _ = fs::remove_file(manifest_path).await;

        match output {
            Ok(res) if res.status.success() => {
                println!("✅ Native Concat complete -> {}", output_path);
                Ok(output_path.to_string())
            }
            Ok(res) => {
                let stderr = String::from_utf8_lossy(&res.stderr);
                Err(format!("FFmpeg failed: {}", stderr))
            }
            Err(e) => Err(format!("Failed to execute FFmpeg: {}", e)),
        }
    }

    /// Keyframe-accurate sub-millisecond trimming without re-encoding (LosslessCut pattern).
    pub async fn slice_video(input_path: &str, start_sec: f64, end_sec: f64, output_path: &str) -> Result<String, String> {
        println!("🦀 [Rust FFmpeg] Slicing '{}' from {:.2}s to {:.2}s...", input_path, start_sec, end_sec);

        let output = Command::new("ffmpeg")
            .arg("-y")
            .arg("-ss")
            .arg(format!("{:.3}", start_sec))
            .arg("-to")
            .arg(format!("{:.3}", end_sec))
            .arg("-i")
            .arg(input_path)
            .arg("-c")
            .arg("copy")
            .arg(output_path)
            .output()
            .await
            .map_err(|e| format!("FFmpeg execution error: {}", e))?;

        if output.status.success() {
            println!("✅ Native Slice complete -> {}", output_path);
            Ok(output_path.to_string())
        } else {
            Err(String::from_utf8_lossy(&output.stderr).to_string())
        }
    }

    /// Native high-fidelity 4K Lanczos super-resolution scaler.
    pub async fn upscale_lanczos(input_path: &str, output_path: &str) -> Result<String, String> {
        println!("🦀 [Rust FFmpeg] 4K Lanczos Scaling '{}' -> '{}'...", input_path, output_path);

        let output = Command::new("ffmpeg")
            .arg("-y")
            .arg("-i")
            .arg(input_path)
            .arg("-vf")
            .arg("scale=3840:2160:flags=lanczos,unsharp=5:5:0.8:5:5:0.0")
            .arg(output_path)
            .output()
            .await
            .map_err(|e| format!("FFmpeg execution error: {}", e))?;

        if output.status.success() {
            println!("✅ 4K Upscale complete -> {}", output_path);
            Ok(output_path.to_string())
        } else {
            Err(String::from_utf8_lossy(&output.stderr).to_string())
        }
    }
}
