mod config;
mod ffmpeg;
mod ipc;
mod server;
mod types;

use clap::{Parser, Subcommand};
use config::EngineConfig;
use ffmpeg::NativeFfmpeg;
use ipc::PythonBridge;

#[derive(Parser, Debug)]
#[command(
    name = "ove",
    author = "Open Video Engine Contributors",
    version = "1.0.0",
    about = "🦀 Open Video Engine (OVE) - Ultra-Fast Native Rust Desktop Engine & Server",
    long_about = "A blazingly fast, memory-safe Rust orchestrator, sub-millisecond FFmpeg stream engine, and local async server for Open Video Engine (OVE)."
)]
struct Cli {
    #[command(subcommand)]
    command: Option<Commands>,

    /// Port to bind the local server to
    #[arg(short, long, default_value_t = 8080)]
    port: u16,
}

#[derive(Subcommand, Debug)]
enum Commands {
    /// Launch the high-speed Tokio + Axum local server
    Serve {
        #[arg(short, long, default_value_t = 8080)]
        port: u16,
    },
    /// Launch the server and open the OVE Pro Studio UI in your default desktop browser
    Run {
        #[arg(short, long, default_value_t = 8080)]
        port: u16,
    },
    /// Losslessly concatenate multiple MP4 files using native FFmpeg concat demuxer (0 re-encoding)
    Concat {
        /// List of MP4 video file paths
        #[arg(required = true)]
        files: Vec<String>,

        /// Destination output file path
        #[arg(short, long, default_value = "out/concatenated_master.mp4")]
        output: String,
    },
    /// Keyframe-accurate precision cutting without re-encoding
    Cut {
        /// Source video file
        input: String,
        /// Start time in seconds (e.g. 0.0 or 12.5)
        start: f64,
        /// End time in seconds (e.g. 5.4 or 24.0)
        end: f64,
        /// Output file path (optional)
        #[arg(short, long)]
        output: Option<String>,
    },
    /// Upscale an image to 4K (3840x2160) using native Lanczos high-fidelity filter
    Upscale {
        input: String,
        #[arg(short, long)]
        output: Option<String>,
    },
    /// Test the IPC bridge connection to the companion Python engine
    Bridge {
        /// Subcommand to forward (e.g. status, presets, advisor)
        #[arg(default_value = "status")]
        cmd: String,
    },
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let cli = Cli::parse();
    let port = cli.port;
    let config = EngineConfig::detect(port);

    match cli.command {
        Some(Commands::Serve { port }) => {
            let mut cfg = config;
            cfg.port = port;
            server::run_server(cfg).await?;
        }
        Some(Commands::Run { port }) => {
            let mut cfg = config;
            cfg.port = port;
            let url = format!("http://127.0.0.1:{}", port);
            println!("🚀 Launching OVE Pro Desktop Studio at {}", url);
            let _ = open::that(&url);
            server::run_server(cfg).await?;
        }
        Some(Commands::Concat { files, output }) => {
            match NativeFfmpeg::concat_videos(&files, &output).await {
                Ok(path) => println!("🎉 Success! Merged video ready at: {}", path),
                Err(err) => eprintln!("❌ Error during concat: {}", err),
            }
        }
        Some(Commands::Cut { input, start, end, output }) => {
            let out_file = output.unwrap_or_else(|| {
                let base = input.trim_end_matches(".mp4");
                format!("{}_cut.mp4", base)
            });
            match NativeFfmpeg::slice_video(&input, start, end, &out_file).await {
                Ok(path) => println!("🎉 Success! Sliced video ready at: {}", path),
                Err(err) => eprintln!("❌ Error during slice: {}", err),
            }
        }
        Some(Commands::Upscale { input, output }) => {
            let out_file = output.unwrap_or_else(|| {
                let base = input.trim_end_matches(".jpg");
                format!("{}_4k.jpg", base)
            });
            match NativeFfmpeg::upscale_lanczos(&input, &out_file).await {
                Ok(path) => println!("🎉 Success! 4K image ready at: {}", path),
                Err(err) => eprintln!("❌ Error during upscale: {}", err),
            }
        }
        Some(Commands::Bridge { cmd }) => {
            let bridge = PythonBridge::new(config);
            match bridge.dispatch_studio(&[&cmd]).await {
                Ok(out) => println!("{}", out),
                Err(err) => eprintln!("{}", err),
            }
        }
        None => {
            // Default action: launch server & open UI
            let url = format!("http://127.0.0.1:{}", port);
            println!("🚀 Launching OVE Pro Desktop Studio at {}", url);
            let _ = open::that(&url);
            server::run_server(config).await?;
        }
    }

    Ok(())
}
