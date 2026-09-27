import { useRef, useState } from "react";
import {
  Bot,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Layers,
  Mic,
  MicOff,
  Send,
  Sparkles,
} from "lucide-react";
import { askAgent } from "../services/aqiService";

export function AgentConsultation({ selectedCity = "Delhi" }) {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [showTools, setShowTools] = useState(true);
  const [isListening, setIsListening] = useState(false);

  const recognitionRef = useRef(null);

  const samplePrompts = [
    `What is the current AQI in ${selectedCity} right now?`,
    `Is it safe for outdoor running in ${selectedCity} today?`,
    `Why is PM2.5 high in ${selectedCity} and what weather causes it?`,
    "Compare the air quality between Delhi and Mumbai.",
  ];

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();

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
        "Voice input is not supported on this device/browser. Please type your query."
      );
      return;
    }

    if (isListening && recognitionRef.current) {
      recognitionRef.current.stop();
      setIsListening(false);
      return;
    }

    const recognition = new SpeechRecognition();

    recognition.lang = "en-IN";
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
          "Microphone permission was denied. Please allow microphone access."
        );
      } else if (event.error === "no-speech") {
        setError("No speech detected. Please try speaking again.");
      } else {
        setError("Voice input failed. Please try again.");
      }
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;
    recognition.start();
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
                isListening ? "Stop listening" : "Speak your question"
              }
              aria-label={
                isListening ? "Stop voice input" : "Start voice input"
              }
              style={{
                position: "absolute",
                right: 12,
                top: 12,
                width: 36,
                height: 36,
                borderRadius: 10,
                border: "1px solid #d8e2dc",
                background: isListening ? "#dcfce7" : "#ffffff",
                color: isListening ? "#15803d" : "#375044",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                cursor: loading ? "not-allowed" : "pointer",
                transition: "all 0.15s ease",
              }}
            >
              {isListening ? <MicOff size={17} /> : <Mic size={17} />}
            </button>
          </div>

          {isListening && (
            <div
              style={{
                marginTop: 8,
                fontSize: 12,
                color: "#15803d",
                display: "flex",
                alignItems: "center",
                gap: 6,
              }}
            >
              <Mic size={14} />
              Listening... Speak your question.
            </div>
          )}

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
                gap: 10,
                marginBottom: 14,
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