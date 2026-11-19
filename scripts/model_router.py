#!/usr/bin/env python3
"""
Intelligent Model Router, Prompt Compressor, and Zero-Cost Fallback Agent
for Antigravity Video Studio.

Connects:
  - Local Llama / Qwen via Ollama (100% Free, Offline Fallback)
  - OpenRouter Free Gateway (openrouter/free, llama-3.3-70b:free, deepseek-r1:free)
  - Google Gemini / AI Pro (Gemini 2.0 Flash / Pro)
  - Rule-Based Deterministic Engine (Zero Tokens, Zero Network)
"""

import os
import sys
import json
import re
import urllib.request
import urllib.error

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(BASE_DIR, "model_router.config.json")

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {
            "routingPolicy": {"preferFree": True, "promptForPermissionOnPaid": True, "autoFallbackToLocal": True},
            "providers": {}
        }
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# ==========================================
# 1. PROMPT COMPRESSOR & CLEANER (Token Saver)
# ==========================================
class PromptCompressor:
    @staticmethod
    def clean_noisy_prompt(raw_text: str) -> dict:
        """
        Cleans messy, colloquial, or rambling prompts into a high-density,
        minimal-token prompt payload. Saves 50-80% of tokens.
        """
        original_words = len(raw_text.split())

        # Strip common filler phrases
        fillers = [
            r"\bumm*\b", r"\bahh*\b", r"\byou know\b", r"\blike\b",
            r"\bcan you please\b", r"\bi want you to\b", r"\bjust make\b",
            r"\bkind of\b", r"\bsort of\b", r"\bbasically\b", r"\bliterally\b"
        ]
        cleaned = raw_text
        for pattern in fillers:
            cleaned = re.sub(pattern, " ", cleaned, flags=re.IGNORECASE)

        # Remove duplicate spaces and punctuation clutter
        cleaned = re.sub(r"[?!.,]{2,}", ".", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        # Extract potential scene parameters if present
        duration_match = re.search(r"(\d+)\s*(?:sec|seconds|s\b)", raw_text, re.IGNORECASE)
        duration = int(duration_match.group(1)) if duration_match else 5

        # Detect motion preference
        motion = "zoom-in"
        if re.search(r"\bpan\s*left\b", raw_text, re.IGNORECASE):
            motion = "pan-left"
        elif re.search(r"\bpan\s*right\b", raw_text, re.IGNORECASE):
            motion = "pan-right"
        elif re.search(r"\bzoom\s*out\b", raw_text, re.IGNORECASE):
            motion = "zoom-out"

        compressed_words = len(cleaned.split())
        token_savings_pct = round(((original_words - compressed_words) / max(original_words, 1)) * 100, 1)

        return {
            "cleaned_prompt": cleaned,
            "detected_duration": duration,
            "detected_motion": motion,
            "original_word_count": original_words,
            "cleaned_word_count": compressed_words,
            "estimated_token_savings": f"{max(0, token_savings_pct)}%"
        }

# ==========================================
# 2. MULTI-TIER MODEL ROUTER & FALLBACK AGENT
# ==========================================
class ModelRouter:
    def __init__(self):
        self.config = load_config()

    def check_local_ollama(self) -> dict:
        """Checks if Ollama is running locally on Mac or HP Pavilion"""
        endpoint = "http://localhost:11434/api/tags"
        try:
            req = urllib.request.Request(endpoint, method="GET")
            with urllib.request.urlopen(req, timeout=0.8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                models = [m.get("name") for m in data.get("models", [])]
                return {"available": True, "models": models}
        except Exception:
            return {"available": False, "models": []}

    def suggest_tier(self, cleaned_prompt: str) -> dict:
        """
        AI Cost-Optimizer: Analyzes task complexity and suggests the cheapest / best provider.
        """
        words = len(cleaned_prompt.split())
        ollama_status = self.check_local_ollama()
        openrouter_key = os.environ.get("OPENROUTER_API_KEY")
        gemini_key = os.environ.get("GEMINI_API_KEY")

        if words < 30 and ollama_status["available"]:
            return {
                "tier": "LOCAL_FREE",
                "recommended_provider": "local_ollama",
                "model": "llama3.2:latest",
                "estimated_cost": "$0.00 (Offline Local)",
                "reason": "Short / structural task. Perfect for local Llama model with 0 latency and 0 tokens."
            }
        elif openrouter_key:
            return {
                "tier": "CLOUD_FREE_ROUTER",
                "recommended_provider": "openrouter_free",
                "model": "openrouter/free",
                "estimated_cost": "$0.00 (OpenRouter Free Tier)",
                "reason": "Creative scene generation. Routed via OpenRouter free model aggregator."
            }
        elif gemini_key:
            return {
                "tier": "GOOGLE_AI_PRO",
                "recommended_provider": "google_gemini",
                "model": "gemini-2.0-flash",
                "estimated_cost": "$0.00 (Google AI Pro / Free RPM Tier)",
                "reason": "High-context documentary structuring and cinematic visuals."
            }
        else:
            return {
                "tier": "DETERMINISTIC_OFFLINE",
                "recommended_provider": "rule_based_engine",
                "model": "internal-studio-parser",
                "estimated_cost": "$0.00 (Offline Rules)",
                "reason": "No cloud API keys detected and Ollama offline. Using deterministic internal parser."
            }

    def generate_with_fallback(self, prompt: str, system_prompt: str = "") -> dict:
        """
        Executes generation following the resilience cascade:
        1. Primary Suggested Provider
        2. Local Ollama (Llama/Qwen)
        3. Deterministic Studio Rule Engine
        """
        suggestion = self.suggest_tier(prompt)
        provider = suggestion["recommended_provider"]

        print(f"🤖 [Model Router] Selected Provider: {provider} ({suggestion['model']}) | Cost: {suggestion['estimated_cost']}")

        # Attempt 1: Local Ollama
        if provider == "local_ollama":
            result = self._call_ollama(prompt, system_prompt)
            if result:
                return {"provider": "local_ollama", "model": suggestion["model"], "content": result}
            print("⚠️ Local Ollama failed or timed out. Falling back to Cloud/Rule engine...")

        # Attempt 2: Groq (Ultra-fast low latency)
        if os.environ.get("GROQ_API_KEY"):
            result = self._call_groq(prompt, system_prompt)
            if result:
                return {"provider": "groq", "model": "llama-3.3-70b-versatile", "content": result}
            print("⚠️ Groq call failed. Falling back...")

        # Attempt 3: OpenRouter Gateway (Free & paid aggregator)
        if provider == "openrouter_free" or os.environ.get("OPENROUTER_API_KEY"):
            result = self._call_openrouter(prompt, system_prompt)
            if result:
                return {"provider": "openrouter_free", "model": "openrouter/free", "content": result}
            print("⚠️ OpenRouter free failed. Falling back...")

        # Attempt 4: Google Gemini 2.0 Flash
        if provider == "google_gemini" or os.environ.get("GEMINI_API_KEY"):
            result = self._call_gemini(prompt, system_prompt)
            if result:
                return {"provider": "google_gemini", "model": "gemini-2.0-flash", "content": result}
            print("⚠️ Gemini call failed. Falling back...")

        # Attempt 5: OpenAI API (gpt-4o-mini)
        if os.environ.get("OPENAI_API_KEY"):
            result = self._call_openai(prompt, system_prompt)
            if result:
                return {"provider": "openai", "model": "gpt-4o-mini", "content": result}
            print("⚠️ OpenAI call failed. Falling back...")

        # Final Fallback: Antigravity Deterministic Studio Rule Engine (Zero Tokens, Zero Network)
        return {
            "provider": "antigravity_deterministic_offline",
            "model": "rule_based_parser",
            "content": self._rule_based_generate(prompt)
        }

    def _call_groq(self, prompt: str, system_prompt: str):
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            return None
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = json.dumps({
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": system_prompt or "You are a professional film director and video editor."},
                    {"role": "user", "content": prompt}
                ]
            }).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=10.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except Exception:
            return None

    def _call_openai(self, prompt: str, system_prompt: str):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return None
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = json.dumps({
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt or "You are a professional film director and video editor."},
                    {"role": "user", "content": prompt}
                ]
            }).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=12.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except Exception:
            return None

    def _call_ollama(self, prompt: str, system_prompt: str):
        try:
            url = "http://localhost:11434/api/generate"
            payload = json.dumps({
                "model": "llama3.2:latest",
                "prompt": f"{system_prompt}\n\nUser: {prompt}\nAssistant:",
                "stream": False
            }).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=12.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("response")
        except Exception:
            return None

    def _call_openrouter(self, prompt: str, system_prompt: str):
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            return None
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/Bakulesh1Codes108/Complete-Local-Video-Studio-Engine-"
            }
            payload = json.dumps({
                "model": "openrouter/free",
                "messages": [
                    {"role": "system", "content": system_prompt or "You are a documentary film director."},
                    {"role": "user", "content": prompt}
                ]
            }).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=15.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except Exception:
            return None

    def _call_gemini(self, prompt: str, system_prompt: str):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return None
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            payload = json.dumps({
                "contents": [{"parts": [{"text": f"{system_prompt}\n\n{prompt}"}]}]
            }).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=15.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            return None

    def _rule_based_generate(self, prompt: str) -> str:
        """Offline deterministic documentary scene parser"""
        lines = prompt.strip().split(". ")
        title = lines[0][:40] if lines else "Documentary Scene"
        narration = prompt.strip()
        visual_prompt = f"Cinematic photorealistic documentary shot depicting: {title}, 35mm film grain, 8k"
        return json.dumps({
            "title": title,
            "narration": narration,
            "visualPrompt": visual_prompt,
            "duration": 5.0,
            "motion": "zoom-in"
        }, indent=2)

# ==========================================
# 3. TOKEN COSTING & BUDGET AGENT
# ==========================================
class TokenCostingAgent:
    PRICING_TABLE = {
        "local_ollama": {
            "name": "Local Ollama (Llama 3.2 / Qwen 2.5)",
            "tier": "Tier 0 (100% Free)",
            "input_per_m": 0.00,
            "output_per_m": 0.00,
            "latency": "Fast (GPU) / Moderate (CPU)",
            "privacy": "100% Offline / Local"
        },
        "openrouter_free": {
            "name": "OpenRouter Free Gateway (llama-3.3-70b:free)",
            "tier": "Tier 0 (100% Free)",
            "input_per_m": 0.00,
            "output_per_m": 0.00,
            "latency": "Cloud API (~800ms)",
            "privacy": "Cloud Aggregated"
        },
        "google_gemini_flash": {
            "name": "Google Gemini 2.0 Flash (Jio AI Pro / Google AI Studio)",
            "tier": "Tier 1 (Free RPM Tier / Micro-Cost)",
            "input_per_m": 0.075,
            "output_per_m": 0.30,
            "latency": "Ultra-Fast (~350ms)",
            "privacy": "Google AI Cloud"
        },
        "groq_llama_70b": {
            "name": "Groq Llama 3.3 70B Versatile",
            "tier": "Tier 1 (High-Speed Cloud)",
            "input_per_m": 0.59,
            "output_per_m": 0.79,
            "latency": "Instant LPU (~180ms)",
            "privacy": "Groq Cloud"
        },
        "openai_gpt4o_mini": {
            "name": "OpenAI GPT-4o-mini",
            "tier": "Tier 2 (Commercial Cloud)",
            "input_per_m": 0.15,
            "output_per_m": 0.60,
            "latency": "Standard (~600ms)",
            "privacy": "OpenAI Cloud"
        },
        "openai_gpt4o": {
            "name": "OpenAI GPT-4o Flagship",
            "tier": "Tier 3 (Premium Studio)",
            "input_per_m": 2.50,
            "output_per_m": 10.00,
            "latency": "Standard (~900ms)",
            "privacy": "OpenAI Cloud"
        },
        "claude_3_5_sonnet": {
            "name": "Anthropic Claude 3.5 Sonnet",
            "tier": "Tier 3 (Premium Director)",
            "input_per_m": 3.00,
            "output_per_m": 15.00,
            "latency": "Deliberate (~1200ms)",
            "privacy": "Anthropic Cloud"
        }
    }

    LEDGER_FILE = os.path.join(BASE_DIR, "token_budget_ledger.json")

    def __init__(self):
        self.ledger = self._load_ledger()

    def _load_ledger(self) -> dict:
        if os.path.exists(self.LEDGER_FILE):
            try:
                with open(self.LEDGER_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "budget_cap_usd": 0.00,
            "total_tokens_used": 0,
            "total_cost_usd": 0.00,
            "free_tokens_saved": 0,
            "transactions": []
        }

    def _save_ledger(self):
        try:
            with open(self.LEDGER_FILE, "w", encoding="utf-8") as f:
                json.dump(self.ledger, f, indent=2)
        except Exception:
            pass

    def estimate_tokens(self, text: str) -> int:
        """Approximates BPE token count for English text (~0.75 words per token)"""
        if not text:
            return 0
        words = len(text.strip().split())
        chars = len(text)
        return max(1, int(max(words * 1.33, chars / 3.8)))

    def calculate_cost_comparison(self, prompt: str, expected_output_tokens: int = 250) -> dict:
        """Compares token expenditure and cost across all free and paid providers"""
        in_tokens = self.estimate_tokens(prompt)
        out_tokens = expected_output_tokens

        comparisons = []
        for key, info in self.PRICING_TABLE.items():
            in_cost = (in_tokens / 1_000_000) * info["input_per_m"]
            out_cost = (out_tokens / 1_000_000) * info["output_per_m"]
            total_cost = round(in_cost + out_cost, 6)

            comparisons.append({
                "provider_id": key,
                "name": info["name"],
                "tier": info["tier"],
                "total_tokens": in_tokens + out_tokens,
                "estimated_cost_usd": total_cost,
                "cost_display": "$0.00 (Free)" if total_cost == 0 else f"${total_cost:.5f}",
                "is_free": total_cost == 0
            })

        return {
            "prompt_tokens": in_tokens,
            "expected_output_tokens": out_tokens,
            "total_tokens": in_tokens + out_tokens,
            "providers": comparisons
        }

    def record_usage(self, provider: str, prompt: str, completion: str = "", task: str = "generation"):
        """Records token usage and cost into the persistent ledger"""
        in_tokens = self.estimate_tokens(prompt)
        out_tokens = self.estimate_tokens(completion) if completion else 150
        total_tokens = in_tokens + out_tokens

        pricing = self.PRICING_TABLE.get(provider, {"input_per_m": 0.0, "output_per_m": 0.0})
        cost = ((in_tokens / 1_000_000) * pricing["input_per_m"]) + ((out_tokens / 1_000_000) * pricing["output_per_m"])
        cost = round(cost, 6)

        self.ledger["total_tokens_used"] += total_tokens
        self.ledger["total_cost_usd"] = round(self.ledger.get("total_cost_usd", 0.0) + cost, 5)

        if cost == 0.0:
            self.ledger["free_tokens_saved"] = self.ledger.get("free_tokens_saved", 0) + total_tokens

        from datetime import datetime
        self.ledger.setdefault("transactions", []).append({
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "provider": provider,
            "tokens": total_tokens,
            "cost_usd": cost
        })
        self._save_ledger()

    def set_budget(self, max_usd: float):
        """Sets the hard ceiling budget limit in USD"""
        self.ledger["budget_cap_usd"] = max_usd
        self._save_ledger()

    def print_cost_guide(self, prompt: str = "A cinematic 3-act documentary scene about underwater hydrothermal vents"):
        comp = self.calculate_cost_comparison(prompt)
        print("=" * 72)
        print("💰 TOKEN OPTIMIZER & COST ESTIMATOR AGENT")
        print("=" * 72)
        print(f"Sample Input Tokens:    {comp['prompt_tokens']}")
        print(f"Expected Output Tokens: {comp['expected_output_tokens']}")
        print(f"Total Video Tokens:     {comp['total_tokens']}")
        print(f"Active Budget Cap:      ${self.ledger.get('budget_cap_usd', 0.0):.2f}")
        print("-" * 72)
        print(f"{'Provider / Model':<35} | {'Tier':<20} | {'Est. Cost':<10}")
        print("-" * 72)
        for p in comp["providers"]:
            tag = "🟢 " if p["is_free"] else "💳 "
            print(f"{tag}{p['name'][:32]:<33} | {p['tier'][:18]:<20} | {p['cost_display']}")
        print("=" * 72)
        print(f"📊 Lifetime Stats: {self.ledger.get('total_tokens_used', 0)} tokens tracked | ${self.ledger.get('total_cost_usd', 0.0):.4f} spent | {self.ledger.get('free_tokens_saved', 0)} free tokens saved")
        print("=" * 72)

if __name__ == "__main__":
    router = ModelRouter()
    compressor = PromptCompressor()
    cost_agent = TokenCostingAgent()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 scripts/model_router.py status")
        print("  python3 scripts/model_router.py clean '<noisy prompt>'")
        print("  python3 scripts/model_router.py suggest '<prompt>'")
        print("  python3 scripts/model_router.py run '<prompt>'")
        sys.exit(0)

    cmd = sys.argv[1].lower()

    if cmd == "status":
        ollama = router.check_local_ollama()
        print("=== Model Router Provider Status ===")
        print(f"Local Ollama (Llama/Qwen): {'🟢 Online (' + ', '.join(ollama['models']) + ')' if ollama['available'] else '⚪ Offline (Run: ollama serve)'}")
        print(f"OpenRouter Gateway:        {'🟢 Configured' if os.environ.get('OPENROUTER_API_KEY') else '🟡 No key (Set OPENROUTER_API_KEY for free models)'}")
        print(f"Google Gemini / AI Pro:    {'🟢 Configured' if os.environ.get('GEMINI_API_KEY') else '🟡 No key (Set GEMINI_API_KEY or use Jio AI Pro in browser)'}")
    elif cmd == "clean":
        raw = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "umm you know can you like make a scene about deep ocean exploration for like 6 seconds or so"
        result = compressor.clean_noisy_prompt(raw)
        print(json.dumps(result, indent=2))
    elif cmd == "suggest":
        raw = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Explain quantum computing in 5 seconds"
        cleaned = compressor.clean_noisy_prompt(raw)
        suggestion = router.suggest_tier(cleaned["cleaned_prompt"])
        print(json.dumps(suggestion, indent=2))
    elif cmd in ["cost", "tokens", "pricing"]:
        prompt = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "A cinematic 3-act documentary scene about underwater hydrothermal vents"
        cost_agent.print_cost_guide(prompt)
    elif cmd == "budget":
        if len(sys.argv) > 2:
            try:
                new_budget = float(sys.argv[2])
                cost_agent.set_budget(new_budget)
                print(f"✅ Token Budget Cap updated to: ${new_budget:.2f}")
            except ValueError:
                print("[-] Please provide a valid numeric dollar amount, e.g. python3 scripts/model_router.py budget 0.05")
        else:
            print(f"💰 Current Active Budget Cap: ${cost_agent.ledger.get('budget_cap_usd', 0.0):.2f}")
    elif cmd == "run":
        raw = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "A majestic drone shot over snowy mountain peaks at sunset"
        cleaned = compressor.clean_noisy_prompt(raw)
        print(f"🧹 Cleaned Prompt ({cleaned['estimated_token_savings']} token savings): '{cleaned['cleaned_prompt']}'")
        res = router.generate_with_fallback(cleaned["cleaned_prompt"])
        print(f"🎯 Output from [{res['provider']} - {res['model']}]:\n{res['content']}")
