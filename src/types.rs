use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Timeline {
    pub project: String,
    pub width: u32,
    pub height: u32,
    pub fps: u32,
    #[serde(default)]
    pub scenes: Vec<Scene>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Scene {
    pub id: String,
    pub title: String,
    pub narration: String,
    pub duration: f64,
    #[serde(rename = "visualPrompt", default)]
    pub visual_prompt: String,
    #[serde(default = "default_motion")]
    pub motion: String,
}

fn default_motion() -> String {
    "zoom-in".to_string()
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CopilotStatus {
    #[serde(rename = "currentStep")]
    pub current_step: u32,
    #[serde(rename = "stepName")]
    pub step_name: String,
    #[serde(rename = "totalSteps")]
    pub total_steps: u32,
    #[serde(rename = "stepsRemaining")]
    pub steps_remaining: u32,
    pub project: String,
    #[serde(rename = "sceneCount")]
    pub scene_count: usize,
    pub format: String,
    #[serde(rename = "safeZone")]
    pub safe_zone: bool,
    pub suggestions: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChatRequest {
    pub message: String,
    #[serde(rename = "currentStep", default = "default_step")]
    pub current_step: u32,
}

fn default_step() -> u32 {
    3
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChatResponse {
    pub status: String,
    pub reply: String,
    pub action: Option<String>,
    #[serde(rename = "currentStep")]
    pub current_step: u32,
    #[serde(rename = "stepsRemaining")]
    pub steps_remaining: u32,
    pub suggestions: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FormatRequest {
    pub format: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ApiResponse {
    pub status: String,
    pub message: String,
}
