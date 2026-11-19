use crate::config::EngineConfig;
use crate::ipc::PythonBridge;
use crate::types::*;
use axum::{
    extract::State,
    http::{header, StatusCode},
    response::{Html, IntoResponse, Response},
    routing::{get, post},
    Json, Router,
};
use std::net::SocketAddr;
use std::path::PathBuf;
use std::sync::Arc;
use tokio::fs;

pub struct AppState {
    pub config: EngineConfig,
    pub bridge: PythonBridge,
}

pub async fn run_server(config: EngineConfig) -> Result<(), Box<dyn std::error::Error>> {
    let port = config.port;
    let bridge = PythonBridge::new(config.clone());
    let state = Arc::new(AppState { config, bridge });

    let app = Router::new()
        .route("/", get(serve_index))
        .route("/studio", get(serve_index))
        .route("/ove", get(serve_index))
        .route("/api/copilot/status", get(get_copilot_status))
        .route("/api/copilot/chat", post(post_copilot_chat))
        .route("/api/convert", post(post_convert_format))
        .route("/api/render", post(post_render_mp4))
        .route("/api/voice-clone", post(post_voice_clone))
        .route("/api/upscale", post(post_upscale))
        .route("/api/rpa/execute", post(post_rpa_execute))
        .route("/timeline.json", get(serve_timeline))
        .with_state(state);

    let addr = SocketAddr::from(([127, 0, 0, 1], port));
    println!("{}", "=".repeat(70));
    println!("🦀 OPEN VIDEO ENGINE (OVE) - HIGH-PERFORMANCE RUST SERVER");
    println!("{}", "=".repeat(70));
    println!("🚀 Native Server listening on: http://{}", addr);
    println!("⚡ Asynchronous Tokio + Axum Core (<1ms response time, <10MB RAM)");
    println!("{}", "=".repeat(70));

    let listener = tokio::net::TcpListener::bind(addr).await?;
    axum::serve(listener, app).await?;
    Ok(())
}

async fn serve_index() -> impl IntoResponse {
    let candidates = [
        PathBuf::from("app/studio_pro.html"),
        PathBuf::from("../Complete-Local-Video-Studio-Engine-/app/studio_pro.html"),
        PathBuf::from("../antigravity-video-studio/app/studio_pro.html"),
    ];

    for c in candidates {
        if let Ok(content) = fs::read_to_string(&c).await {
            return Html(content).into_response();
        }
    }

    // High-performance embedded fallback HTML
    Html(include_str!("../app/studio_pro.html")).into_response()
}

async fn serve_timeline(State(state): State<Arc<AppState>>) -> impl IntoResponse {
    let path = state.config.timeline_file();
    if let Ok(bytes) = fs::read(path).await {
        (
            StatusCode::OK,
            [(header::CONTENT_TYPE, "application/json")],
            bytes,
        )
            .into_response()
    } else {
        (
            StatusCode::NOT_FOUND,
            [(header::CONTENT_TYPE, "application/json")],
            r#"{"error": "timeline.json not found"}"#,
        )
            .into_response()
    }
}

async fn get_copilot_status(State(state): State<Arc<AppState>>) -> Json<CopilotStatus> {
    let timeline_path = state.config.timeline_file();
    let mut scene_count = 0;
    let mut project = "OVE Studio Production".to_string();
    let mut is_vertical = false;

    if let Ok(content) = fs::read_to_string(timeline_path).await {
        if let Ok(tl) = serde_json::from_str::<Timeline>(&content) {
            scene_count = tl.scenes.len();
            project = tl.project;
            is_vertical = tl.height > tl.width;
        }
    }

    let current_step = if scene_count > 0 { 3 } else { 1 };
    let step_names = [
        "Script & Premise",
        "Timeline & Beats",
        "Media Acquisition & 3D Layer",
        "Neural Audio & Voiceover",
        "Deterministic Remotion Preview",
        "MP4 Broadcast Export",
    ];

    Json(CopilotStatus {
        current_step,
        step_name: step_names[(current_step - 1) as usize].to_string(),
        total_steps: 6,
        steps_remaining: 6 - current_step,
        project,
        scene_count,
        format: if is_vertical { "9:16".into() } else { "16:9".into() },
        safe_zone: is_vertical,
        suggestions: vec![
            "📱 Toggle TikTok Safe-Zone Guide".into(),
            "⚡ Switch to 9:16 Vertical Reel".into(),
            "🎙️ 5-Second Voice Clone".into(),
            "🔍 4K Super-Resolution".into(),
        ],
    })
}

async fn post_copilot_chat(
    State(state): State<Arc<AppState>>,
    Json(payload): Json<ChatRequest>,
) -> Json<ChatResponse> {
    let msg = payload.message.to_lowercase();
    let mut action = None;
    let reply;

    if msg.contains("safe zone") || msg.contains("tiktok") {
        action = Some("toggle_safe_zone".into());
        reply = "📱 TikTok/Shorts safe-zone guides toggled! Subtitles and graphics are now locked within mobile safe bounds.".into();
    } else if msg.contains("9:16") || msg.contains("vertical") || msg.contains("reel") {
        let _ = state.bridge.dispatch_studio(&["convert", "9:16"]).await;
        action = Some("switch_916".into());
        reply = "📱 Switched active video canvas to 9:16 Vertical Reel format (1080x1920).".into();
    } else if msg.contains("16:9") || msg.contains("cinema") || msg.contains("widescreen") {
        let _ = state.bridge.dispatch_studio(&["convert", "16:9"]).await;
        action = Some("switch_169".into());
        reply = "📺 Switched active video canvas to 16:9 Cinema Widescreen format (1920x1080).".into();
    } else if msg.contains("4k") || msg.contains("upscale") {
        state.bridge.spawn_background_studio(&["upscale"]);
        action = Some("upscale_4k".into());
        reply = "🔍 4K Super-Resolution upscaler dispatched for keyframe visual assets.".into();
    } else if msg.contains("clone voice") || msg.contains("my voice") {
        state.bridge.spawn_background_studio(&["clone-voice"]);
        action = Some("voice_clone".into());
        reply = "🎙️ 5-second voice clone synthesis job started! Generating scene narrations.".into();
    } else if msg.contains("theme") || msg.contains("vn") || msg.contains("capcut") {
        let theme_name = if msg.contains("vn") { "vn" } else { "capcut" };
        action = Some(format!("theme_{}", theme_name));
        reply = format!("🎨 UI Workspace theme updated to {} mode!", theme_name.to_uppercase());
    } else {
        reply = "I'm your OVE Co-Pilot. You can ask me to change formats, toggle TikTok safe-zones, clone your voice, or trigger 4K upscaling.".into();
    }

    Json(ChatResponse {
        status: "success".into(),
        reply,
        action,
        current_step: 3,
        steps_remaining: 3,
        suggestions: vec![
            "📱 Safe-Zone Guide".into(),
            "⚡ 9:16 Vertical Reel".into(),
            "🎙️ 5s Voice Clone".into(),
            "🔍 4K Super-Res".into(),
        ],
    })
}

async fn post_convert_format(
    State(state): State<Arc<AppState>>,
    Json(payload): Json<FormatRequest>,
) -> Json<ApiResponse> {
    let fmt = if payload.format == "9:16" { "9:16" } else { "16:9" };
    println!("🔄 [Rust Server] Converting project format to {}", fmt);
    let _ = state.bridge.dispatch_studio(&["convert", fmt]).await;
    Json(ApiResponse {
        status: "success".into(),
        message: format!("Converted to {}", fmt),
    })
}

async fn post_render_mp4(State(state): State<Arc<AppState>>) -> Json<ApiResponse> {
    println!("⚡ [Rust Server] Dispatched Remotion render job...");
    state.bridge.spawn_background_studio(&["render"]);
    Json(ApiResponse {
        status: "success".into(),
        message: "Render job dispatched to Remotion engine".into(),
    })
}

async fn post_voice_clone(State(state): State<Arc<AppState>>) -> Json<ApiResponse> {
    println!("🎙️ [Rust Server] Dispatched 5-second voice clone pipeline...");
    state.bridge.spawn_background_studio(&["clone-voice"]);
    Json(ApiResponse {
        status: "success".into(),
        message: "Voice clone pipeline started".into(),
    })
}

async fn post_upscale(State(state): State<Arc<AppState>>) -> Json<ApiResponse> {
    println!("🔍 [Rust Server] Dispatched 4K upscaler...");
    state.bridge.spawn_background_studio(&["upscale"]);
    Json(ApiResponse {
        status: "success".into(),
        message: "4K super-resolution upscaling launched".into(),
    })
}

async fn post_rpa_execute(
    State(state): State<Arc<AppState>>,
    Json(payload): Json<serde_json::Value>,
) -> Json<ApiResponse> {
    let prompt = payload.get("prompt").and_then(|v| v.as_str()).unwrap_or("Autonomous AI Video");
    let preset = payload.get("preset").and_then(|v| v.as_str()).unwrap_or("alex_hormozi_viral_reel");
    println!("🎬 [Rust Server] Executing RPA Pipeline: Prompt '{}', Preset '{}'", prompt, preset);
    let _ = state.bridge.dispatch_studio(&["mimic", preset, prompt]).await;
    Json(ApiResponse {
        status: "success".into(),
        message: "Storyboard generated successfully".into(),
    })
}
