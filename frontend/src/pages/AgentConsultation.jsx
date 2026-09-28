import { useEffect, useRef, useState } from "react";
import { Capacitor } from "@capacitor/core";
import { TextToSpeech } from "@capacitor-community/text-to-speech";
import {
  Bot,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Globe,
  Layers,
  Mic,
  MicOff,
  Send,
  Sparkles,
  Square,
  Volume2,
} from "lucide-react";
import { askAgent } from "../services/aqiService";

function cleanMarkdownForSpeech(markdown) {
  if (!markdown) return "";
  return markdown
    .replace(/^#{1,6}\s+/gm, "")
    .replace(/\|/g, " ")
    .replace(/:?---+:?/g, "")
    .replace(/\*\*(.*?)\*\*/g, "$1")
    .replace(/\*(.*?)\*/g, "$1")
    .replace(/```[\s\S]*?```/g, "")
    .replace(/`([^`]+)`/g, "$1")
    .replace(/^\s*[-*+]\s+/gm, "")
    .replace(/\$(.*?)\$/g, "$1")
    .replace(
      /[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{1F700}-\u{1F77F}\u{1F780}-\u{1F7FF}\u{1F800}-\u{1F8FF}\u{1F900}-\u{1F9FF}\u{1FA00}-\u{1FA6F}\u{1FA70}-\u{1FAFF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/gu,
      ""
    )
    .replace(/\n+/g, ". ")
    .replace(/\s+/g, " ")
    .replace(/\.\s*\./g, ".")
    .trim();
}

const LANGUAGE_OPTIONS = [
  { id: "en-IN", label: "English (IN)", tag: "en-IN", hint: "English recognition" },
  { id: "hi-IN", label: "हिन्दी (Hindi)", tag: "hi-IN", hint: "हिंदी बोली पहचान" },
  { id: "hinglish", label: "Hinglish", tag: "en-IN", hint: "Hinglish voice input" },
];

export function AgentConsultation({ selectedCity = "Delhi" }) {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [showTools, setShowTools] = useState(true);
  const [isListening, setIsListening] = useState(false);
  const [speechLang, setSpeechLang] = useState("en-IN");
  const [isSpeaking, setIsSpeaking] = useState(false);

  const recognitionRef = useRef(null);
  const utteranceRef = useRef(null);

  const samplePrompts = [
    `What is the current AQI in ${selectedCity} right now?`,
    `Is it safe for outdoor running in ${selectedCity} today?`,
    `क्या ${selectedCity} में आज बाहर जाना सुरक्षित है?`,
    `Delhi mein aaj pollution kaisa hai?`,
    `Why is PM2.5 high in ${selectedCity} and what weather causes it?`,
    "Compare the air quality between Delhi and Mumbai.",
  ];

  const stopAnySpeech = async () => {
    if (Capacitor.isNativePlatform()) {
      try {
        await TextToSpeech.stop();
      } catch {
        // ignore stop errors
      }
    } else if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
    setIsSpeaking(false);
  };

  // Prefetch TTS voices and handle cleanup on component unmount
  useEffect(() => {
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      const loadVoices = () => {
        window.speechSynthesis.getVoices();
      };
      loadVoices();
      window.speechSynthesis.onvoiceschanged = loadVoices;
    }

    return () => {
      stopAnySpeech();
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch {
          // ignore
        }
      }
    };
  }, []);

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();

    await stopAnySpeech();

    if (!query.trim()) {
      setError("Please enter a question for the AI Agent.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const data = await askAgent(query);
      setResult(data);
    } catch (err) {
      setError(err.message || "Agent consultation failed.");
    } finally {
      setLoading(false);
    }
  };

  const handleQuickPrompt = (promptText) => {
    setQuery(promptText);
    setError("");
  };

  const handleVoiceInput = () => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setError(
        "Voice input is not supported on this browser/device. Please type your query."
      );
      return;
    }

    if (isListening && recognitionRef.current) {
      recognitionRef.current.stop();
      setIsListening(false);
      return;
    }

    const recognition = new SpeechRecognition();
    const activeLangConfig =
      LANGUAGE_OPTIONS.find((opt) => opt.id === speechLang) || LANGUAGE_OPTIONS[0];

    recognition.lang = activeLangConfig.tag;
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => {
      setIsListening(true);
      setError("");
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;

      setQuery((previousQuery) =>
        previousQuery.trim()
          ? `${previousQuery.trim()} ${transcript}`
          : transcript
      );
    };

    recognition.onerror = (event) => {
      setIsListening(false);

      if (event.error === "not-allowed") {
        setError(
          "Microphone permission was denied. Please allow microphone access in browser or app settings."
        );
      } else if (event.error === "no-speech") {
        setError("No speech detected. Please try speaking again.");
      } else if (event.error === "audio-capture") {
        setError("No microphone detected. Please check your audio input device.");
      } else {
        setError("Voice input failed. Please try again or type your question.");
      }
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;
    try {
      recognition.start();
    } catch (err) {
      console.warn("Speech recognition start failed:", err);
      setIsListening(false);
    }
  };

  const handleToggleSpeech = async () => {
    if (isSpeaking) {
      await stopAnySpeech();
      return;
    }

    if (!result || !result.response) {
      return;
    }

    const spokenText = cleanMarkdownForSpeech(result.response);
    if (!spokenText) return;

    const isHindi =
      /[\u0900-\u097F]/.test(result.response) || speechLang === "hi-IN";

    // Native Android execution via Capacitor Text-to-Speech plugin
    if (Capacitor.isNativePlatform()) {
      try {
        await TextToSpeech.stop();
      } catch {
        // ignore stop errors
      }

      setIsSpeaking(true);
      setError("");

      try {
        await TextToSpeech.speak({
          text: spokenText,
          lang: isHindi ? "hi-IN" : "en-IN",
          rate: 0.96,
          pitch: 1.0,
        });
      } catch (nativeErr) {
        console.warn("Native TTS playback error:", nativeErr);
        setError(
          "Android Text-to-Speech playback failed. Please verify device TTS settings."
        );
      } finally {
        setIsSpeaking(false);
      }
      return;
    }

    // Web Browser execution via Web Speech API
    if (typeof window === "undefined" || !("speechSynthesis" in window)) {
      setError("Text-to-Speech is not supported in this browser or device.");
      return;
    }

    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(spokenText);
    utteranceRef.current = utterance;

    const voices = window.speechSynthesis.getVoices() || [];

    if (isHindi) {
      utterance.lang = "hi-IN";
      const hindiVoice = voices.find(
        (v) =>
          v.lang.toLowerCase().startsWith("hi") ||
          v.name.toLowerCase().includes("hindi")
      );
      if (hindiVoice) {
        utterance.voice = hindiVoice;
      }
    } else {
      utterance.lang = "en-IN";
      const indianVoice = voices.find(
        (v) =>
          v.lang.toLowerCase() === "en-in" ||
          v.lang.toLowerCase().replace("_", "-") === "en-in" ||
          v.name.toLowerCase().includes("india")
      );
      if (indianVoice) {
        utterance.voice = indianVoice;
      } else {
        const genericVoice = voices.find((v) =>
          v.lang.toLowerCase().startsWith("en")
        );
        if (genericVoice) {
          utterance.voice = genericVoice;
        }
      }
    }

    utterance.rate = 0.96;
    utterance.pitch = 1.0;

    utterance.onstart = () => {
      setIsSpeaking(true);
    };

    utterance.onend = () => {
      setIsSpeaking(false);
    };

    utterance.onerror = (e) => {
      console.warn("Speech synthesis error:", e);
      setIsSpeaking(false);
    };

    window.speechSynthesis.speak(utterance);
  };

  return (
    <div
      className="agent-page"
      style={{ display: "flex", flexDirection: "column", gap: 20 }}
    >
      {/* HERO BANNER */}
      <section className="model-hero">
        <div className="model-hero-content">
          <div className="model-hero-icon">
            <Sparkles size={30} />
          </div>

          <div>
            <div className="model-status">
              <span></span>
              Multi-Tool ReAct Agent
            </div>

            <h3>Air Quality Intelligence Agent</h3>

            <p>
              An autonomous decision-making agent that plans, selects tools,
              fetches live sensor and weather telemetry, queries historical
              baselines, and generates actionable advisories.
            </p>
          </div>
        </div>

        <div className="model-hero-side">
          <span>ORCHESTRATION</span>
          <strong>Deterministic + LLM</strong>
          <small>Zero-key fallback enabled</small>
        </div>
      </section>

      {/* QUERY INPUT SECTION */}
      <div className="form-card">
        <div className="prediction-title-row">
          <div>
            <p className="label">NATURAL LANGUAGE CONSULTATION</p>
            <h3>Ask the Air Quality Advisor</h3>
          </div>

          <div className="prediction-icon">
            <Bot size={22} />
          </div>
        </div>

        <p className="form-description">
          Inquire about current health risks, outdoor exercise safety, weather
          dispersion, or seasonal pollution patterns. The agent will
          orchestrate relevant tools to answer.
        </p>

        {/* SAMPLE PROMPT CHIPS */}
        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: 8,
            marginTop: 16,
          }}
        >
          {samplePrompts.map((prompt) => (
            <button
              key={prompt}
              type="button"
              onClick={() => handleQuickPrompt(prompt)}
              style={{
                background: "#f0f5ee",
                border: "1px solid #dbe6d7",
                borderRadius: 16,
                padding: "6px 12px",
                fontSize: 11,
                color: "#2a4939",
                cursor: "pointer",
                transition: "all 0.15s ease",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = "#9ecf42";
                e.currentTarget.style.background = "#eef7df";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = "#dbe6d7";
                e.currentTarget.style.background = "#f0f5ee";
              }}
            >
              💡 {prompt}
            </button>
          ))}
        </div>

        <form onSubmit={handleSubmit} style={{ marginTop: 18 }}>
          <div style={{ position: "relative" }}>
            <textarea
              rows={3}
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                setError("");
              }}
              placeholder={`e.g., "Is it safe for an asthma patient to go outdoors in ${selectedCity} this evening?"`}
              style={{
                width: "100%",
                padding: "14px 58px 14px 16px",
                borderRadius: 12,
                border: "1px solid #d8e2dc",
                background: "#fbfcfb",
                fontFamily: "inherit",
                fontSize: 13,
                outline: "none",
                resize: "vertical",
                boxSizing: "border-box",
              }}
            />

            {/* VOICE INPUT BUTTON */}
            <button
              type="button"
              onClick={handleVoiceInput}
              disabled={loading}
              title={
                isListening ? "Stop listening" : `Speak your question (${LANGUAGE_OPTIONS.find((o) => o.id === speechLang)?.label || "Voice"})`
              }
              aria-label={
                isListening ? "Stop voice input" : "Start voice input"
              }
              style={{
                position: "absolute",
                right: 12,
                top: 12,
                width: 38,
                height: 38,
                borderRadius: 10,
                border: isListening ? "2px solid #22c55e" : "1px solid #d8e2dc",
                background: isListening ? "#dcfce7" : "#ffffff",
                color: isListening ? "#15803d" : "#375044",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                cursor: loading ? "not-allowed" : "pointer",
                boxShadow: isListening ? "0 0 12px rgba(34, 197, 94, 0.4)" : "none",
                transition: "all 0.2s ease",
              }}
            >
              {isListening ? <MicOff size={18} /> : <Mic size={18} />}
            </button>
          </div>

          {/* VOICE LANGUAGE SELECTOR & STATUS BAR */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              flexWrap: "wrap",
              gap: 8,
              marginTop: 10,
              padding: "2px 2px",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 6,
                fontSize: 11.5,
                color: "#4d6357",
              }}
            >
              <Globe size={13} style={{ color: "#1f8f63" }} />
              <span style={{ fontWeight: 600 }}>Voice Input:</span>
              <div style={{ display: "flex", gap: 5 }}>
                {LANGUAGE_OPTIONS.map((opt) => {
                  const isSelected = speechLang === opt.id;
                  return (
                    <button
                      key={opt.id}
                      type="button"
                      onClick={() => setSpeechLang(opt.id)}
                      title={opt.hint}
                      style={{
                        background: isSelected ? "#1f8f63" : "#f0f5ee",
                        color: isSelected ? "#ffffff" : "#2a4939",
                        border: `1px solid ${isSelected ? "#1f8f63" : "#dbe6d7"}`,
                        borderRadius: 14,
                        padding: "3px 9px",
                        fontSize: 11,
                        fontWeight: isSelected ? 600 : 400,
                        cursor: "pointer",
                        transition: "all 0.15s ease",
                      }}
                    >
                      {opt.label}
                    </button>
                  );
                })}
              </div>
            </div>

            {isListening && (
              <div
                style={{
                  fontSize: 12,
                  color: "#15803d",
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                  fontWeight: 600,
                  background: "#dcfce7",
                  padding: "3px 10px",
                  borderRadius: 12,
                }}
              >
                <span
                  style={{
                    width: 7,
                    height: 7,
                    borderRadius: "50%",
                    background: "#16a34a",
                    display: "inline-block",
                  }}
                />
                Listening ({LANGUAGE_OPTIONS.find((o) => o.id === speechLang)?.label})... Speak now
              </div>
            )}
          </div>

          {error && <div className="form-error">{error}</div>}

          <div className="form-actions" style={{ marginTop: 14 }}>
            <button
              type="submit"
              className="primary-button"
              disabled={loading}
              style={{ padding: "12px 24px" }}
            >
              {loading ? (
                <>
                  <div
                    style={{
                      width: 14,
                      height: 14,
                      border: "2px solid rgba(255,255,255,0.4)",
                      borderTopColor: "#fff",
                      borderRadius: "50%",
                      animation: "spin 0.6s linear infinite",
                      marginRight: 6,
                    }}
                  ></div>
                  Orchestrating Agent Tools...
                </>
              ) : (
                <>
                  <Send size={15} />
                  Consult Agent
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* RESULTS DISPLAY */}
      {result && (
        <div style={{ display: "grid", gap: 18 }}>
          {/* Tool Execution Trace Card */}
          {result.activity && result.activity.length > 0 && (
            <div
              style={{
                background: "#ffffff",
                border: "1px solid #dce5df",
                borderRadius: 16,
                padding: "18px 22px",
                boxShadow: "0 4px 16px rgba(22, 47, 36, 0.03)",
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  cursor: "pointer",
                }}
                onClick={() => setShowTools(!showTools)}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 8,
                  }}
                >
                  <Layers size={18} style={{ color: "#1f8f63" }} />

                  <span
                    style={{
                      fontWeight: 700,
                      fontSize: 13,
                      color: "#10231c",
                    }}
                  >
                    Agent Execution Trace ({result.activity.length} Tools
                    Invoked)
                  </span>
                </div>

                <button
                  type="button"
                  style={{
                    background: "none",
                    border: "none",
                    cursor: "pointer",
                    color: "#71847b",
                  }}
                >
                  {showTools ? (
                    <ChevronUp size={16} />
                  ) : (
                    <ChevronDown size={16} />
                  )}
                </button>
              </div>

              {showTools && (
                <div
                  style={{
                    marginTop: 12,
                    display: "grid",
                    gap: 8,
                  }}
                >
                  {result.activity.map((step, idx) => (
                    <div
                      key={idx}
                      style={{
                        display: "flex",
                        alignItems: "flex-start",
                        gap: 10,
                        fontSize: 12,
                        color: "#375044",
                        background: "#f7faf7",
                        padding: "8px 12px",
                        borderRadius: 8,
                        border: "1px solid #e5eee8",
                      }}
                    >
                      <CheckCircle2
                        size={15}
                        style={{
                          color: "#15803d",
                          flexShrink: 0,
                          marginTop: 1,
                        }}
                      />

                      <span>{step}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Synthesized Answer Card */}
          <div
            style={{
              background: "#ffffff",
              border: "1px solid #dce5df",
              borderRadius: 18,
              padding: "24px 28px",
              boxShadow: "0 8px 24px rgba(22, 47, 36, 0.04)",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                flexWrap: "wrap",
                gap: 10,
                marginBottom: 14,
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                }}
              >
                <div
                  style={{
                    width: 36,
                    height: 36,
                    borderRadius: 10,
                    background: "#edf7df",
                    color: "#5e8039",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                >
                  <Bot size={20} />
                </div>

                <div>
                  <h4 style={{ margin: 0, fontSize: 16 }}>
                    Agent Synthesis
                  </h4>

                  <small style={{ color: "#71847b" }}>
                    Grounded with live sensor &amp; model data
                  </small>
                </div>
              </div>

              {/* TEXT-TO-SPEECH READ ALOUD BUTTON */}
              <button
                type="button"
                onClick={handleToggleSpeech}
                title={isSpeaking ? "Stop speaking" : "Listen to answer aloud"}
                aria-label={isSpeaking ? "Stop reading answer" : "Read answer aloud"}
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 6,
                  background: isSpeaking ? "#fee2e2" : "#f0f5ee",
                  color: isSpeaking ? "#b91c1c" : "#2a4939",
                  border: `1px solid ${isSpeaking ? "#fca5a5" : "#dbe6d7"}`,
                  borderRadius: 20,
                  padding: "6px 14px",
                  fontSize: 12,
                  fontWeight: 600,
                  cursor: "pointer",
                  transition: "all 0.15s ease",
                }}
              >
                {isSpeaking ? (
                  <>
                    <Square size={13} style={{ fill: "#b91c1c" }} />
                    <span>Stop</span>
                  </>
                ) : (
                  <>
                    <Volume2 size={15} />
                    <span>Listen</span>
                  </>
                )}
              </button>
            </div>

            {isSpeaking && (
              <div
                style={{
                  fontSize: 12,
                  color: "#15803d",
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                  marginBottom: 14,
                  background: "#f0fdf4",
                  padding: "6px 12px",
                  borderRadius: 8,
                  border: "1px solid #bbf7d0",
                }}
              >
                <Volume2 size={14} />
                <span>Reading response aloud... Click Stop anytime.</span>
              </div>
            )}

            <div
              style={{
                fontSize: 13.5,
                lineHeight: 1.7,
                color: "#1e372b",
                whiteSpace: "pre-wrap",
                fontFamily: "inherit",
              }}
            >
              {result.response}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AgentConsultation;