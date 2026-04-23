import React, { useEffect, useMemo, useRef, useState } from "react";
import {
  Bot,
  ChevronRight,
  CirclePlay,
  Droplets,
  Flame,
  Leaf,
  Mic,
  Send,
  Salad,
  Sparkles,
  Volume2,
  Wand2,
  X,
} from "lucide-react";

const SPICES = [
  { name: "paprika", icon: Flame },
  { name: "cumin", icon: Sparkles },
  { name: "pepper", icon: Wand2 },
  { name: "salt", icon: Droplets },
  { name: "oregano", icon: Leaf },
  { name: "flakes", icon: Salad },
];

function cn(...classes) {
  return classes.filter(Boolean).join(" ");
}

function AssistantBubble({ role, children }) {
  const isUser = role === "user";
  return (
    <div className={cn("flex", isUser ? "justify-end" : "justify-start")}>
      <div
        className={cn(
          "max-w-[76%] rounded-[1.5rem] border px-4 py-3 text-sm leading-relaxed shadow-lg backdrop-blur-md",
          isUser
            ? "border-white/12 bg-white/10 text-white"
            : "border-cyan-300/18 bg-cyan-300/10 text-slate-50"
        )}
      >
        {children}
      </div>
    </div>
  );
}

function SpiceCard({ spice, active, onClick }) {
  const Icon = spice.icon;
  return (
    <button
      type="button"
      onClick={() => onClick(spice.name)}
      className={cn(
        "group relative overflow-hidden rounded-[1.7rem] border px-4 py-4 text-left transition duration-200",
        "bg-white/5 border-white/10 hover:border-cyan-300/30 hover:bg-white/7",
        active && "border-cyan-300/60 bg-cyan-300/14 shadow-[0_0_26px_rgba(34,211,238,0.18)]"
      )}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-cyan-400/6 to-fuchsia-500/6 opacity-0 transition group-hover:opacity-100" />
      <div className="relative flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl border border-white/10 bg-black/20">
            <Icon className="h-4 w-4 text-cyan-100" />
          </div>
          <div>
            <div className="text-[15px] font-semibold capitalize text-white">{spice.name}</div>
            <div className="mt-1 text-xs text-slate-400">Pre-loaded spice</div>
          </div>
        </div>
        <ChevronRight className={cn("h-4 w-4", active ? "text-cyan-100" : "text-slate-500")} />
      </div>
    </button>
  );
}

function QuickChip({ spice, onClick }) {
  return (
    <button
      type="button"
      onClick={() => onClick(spice)}
      className="rounded-full border border-cyan-300/18 bg-cyan-300/10 px-3 py-1.5 text-xs font-medium capitalize text-cyan-100 transition hover:bg-cyan-300/16"
    >
      Use {spice}
    </button>
  );
}

function getStepDescription(i, total) {
  if (i === 0) return "Builds the base flavor";
  if (i === total - 1) return "Finishes and balances the dish";
  return "Adds depth and complexity";
}

function getStepLabel(i, total) {
  if (i === 0) return "Base";
  if (i === total - 1) return "Finish";
  return "Layer";
}

function RecipeCard({ recipe, selectedSpice, onDispenseAll, onReplaceStep, onRemoveStep }) {
  return (
    <div className="rounded-[2rem] border border-white/10 bg-black/25 p-4 shadow-lg">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="text-lg font-semibold text-white">{recipe.title}</div>
          <div className="mt-1 text-sm text-slate-300">{recipe.summary}</div>
          <div className="mt-2 text-xs uppercase tracking-[0.22em] text-slate-500">
            Servings: {recipe.servings ?? "?"}
          </div>
        </div>

        <button
          type="button"
          onClick={onDispenseAll}
          className="inline-flex items-center gap-2 rounded-full bg-white px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-100"
        >
          <CirclePlay className="h-4 w-4" />
          Dispense recipe
        </button>
      </div>

      <div className="mt-4 space-y-2">
        {recipe.steps.map((step, idx) => (
          <div
            key={`${step.spice}-${idx}`}
            className="flex items-center justify-between gap-3 rounded-[1.25rem] border border-white/10 bg-white/5 px-4 py-3"
          >
            <div>
              <div className="text-sm font-medium text-white">
                <span className="capitalize font-semibold">
                  {getStepLabel(idx, recipe.steps.length)} — {step.spice}
                </span>
              </div>
              <div className="mt-1 text-xs text-slate-400">
                {step.description || getStepDescription(idx, recipe.steps.length)}
              </div>
            </div>
            <div className="flex items-center gap-2">
              <select
                value={step.spice}
                onChange={(e) => onReplaceStep(idx, e.target.value)}
                className="rounded-full border border-cyan-300/18 bg-cyan-300/10 px-3 py-1.5 text-xs text-cyan-100"
              >
                {SPICES.map((s) => (
                  <option key={s.name} value={s.name}>
                    {s.name}
                  </option>
                ))}
              </select>
              <button
                type="button"
                onClick={() => onRemoveStep(idx)}
                className="rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-slate-300 transition hover:bg-white/10"
              >
                Remove
              </button>
            </div>
          </div>
        ))}
      </div>

      {recipe.notes?.length ? (
        <div className="mt-4 rounded-[1.25rem] border border-cyan-300/12 bg-cyan-300/8 p-3">
          <div className="text-xs uppercase tracking-[0.22em] text-cyan-200">Notes</div>
          <ul className="mt-2 space-y-1 text-sm text-slate-300">
            {recipe.notes.map((note, idx) => (
              <li key={idx}>• {note}</li>
            ))}
          </ul>
        </div>
      ) : null}
    </div>
  );
}

export default function App() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "Tell Shroom what you want to make, and I’ll build a recipe card you can revise.",
    },
  ]);
  const [input, setInput] = useState("");
  const [selectedSpice, setSelectedSpice] = useState("cumin");
  const [recipe, setRecipe] = useState(null);
  const [pendingAction, setPendingAction] = useState(null); // { kind: 'spice' | 'recipe', label: string }
  const [statusText, setStatusText] = useState("ready");
  const [voiceMode, setVoiceMode] = useState(false);
  const [listening, setListening] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);

  const actionTimerRef = useRef(null);
  const chatRef = useRef(null);
  const recognitionRef = useRef(null);
  const voiceModeRef = useRef(false);
  const lastAssistantRef = useRef("");

  const selectedSpiceObj = useMemo(
    () => SPICES.find((s) => s.name === selectedSpice) ?? SPICES[0],
    [selectedSpice]
  );

  useEffect(() => {
    if (!chatRef.current) return;

    chatRef.current.scrollTo({
      top: chatRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages, recipe]);

  useEffect(() => {
    voiceModeRef.current = voiceMode;
  }, [voiceMode]);

  useEffect(() => {
    setSpeechSupported(Boolean(window.SpeechRecognition || window.webkitSpeechRecognition));
  }, []);

  useEffect(() => {
    return () => {
      if (actionTimerRef.current) clearTimeout(actionTimerRef.current);
    };
  }, []);

  function speak(text) {
    if (typeof window === "undefined" || !("speechSynthesis" in window) || !text) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1;
    utterance.pitch = 1;
    utterance.lang = "en-US";
    window.speechSynthesis.speak(utterance);
  }

  function appendAssistant(text) {
    lastAssistantRef.current = text;
    setMessages((prev) => [...prev, { role: "assistant", content: text }]);
    speak(text);
  }

  function speakRecipe(recipeObj) {
    if (!recipeObj?.steps?.length) return;

    const stepText = recipeObj.steps
      .map((step, idx) => {
        const desc = step.description || getStepDescription(idx, recipeObj.steps.length);
        return `Step ${idx + 1}: ${step.spice}. ${desc}.`;
      })
      .join(" ");

    speak(`${recipeObj.title}. ${recipeObj.summary}. ${stepText}`);
  }

  async function sendUserRequest(text) {
    const clean = text.trim();
    if (!clean) return;

    setMessages((prev) => [...prev, { role: "user", content: clean }]);
    setInput("");
    setStatusText("thinking");

    try {
      const res = await fetch("/api/recipe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: clean, current_recipe: recipe }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data?.error || "Request failed");
      }

      appendAssistant(data.assistant_message);
      setRecipe(data.recipe || null);
      setStatusText("recipe ready");
      if (voiceModeRef.current) speak("Recipe ready.");
    } catch (error) {
      appendAssistant("I could not generate a recipe right now.");
      setStatusText("error");
    }
  }

  async function handleSend(e) {
    e.preventDefault();
    await sendUserRequest(input);
  }

  function handleVoiceText(transcript) {
    const clean = transcript.trim();
    const lower = clean.toLowerCase();

    if (!clean) return;

    if (/(cancel|stop listening)/.test(lower)) {
      cancelPending();
      speak("Canceled.");
      return;
    }

    if (/repeat/.test(lower)) {
      speak(lastAssistantRef.current || "Nothing to repeat.");
      return;
    }

    if (recipe && /(read recipe|read the recipe)/.test(lower)) {
      speakRecipe(recipe);
      return;
    }

    if (recipe && /(dispense recipe|dispense all|all spices)/.test(lower)) {
      dispenseRecipe(recipe);
      return;
    }

    if (/(dispense selected|dispense spice)/.test(lower)) {
      manualDispense(selectedSpiceObj.name);
      return;
    }

    void sendUserRequest(clean);
  }

  function startVoiceMode() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      appendAssistant("Voice input is not available in this browser.");
      setStatusText("voice unavailable");
      return;
    }

    if (!recognitionRef.current) {
      const recognition = new SpeechRecognition();
      recognition.lang = "en-US";
      recognition.interimResults = false;
      recognition.continuous = false;

      recognition.onresult = (event) => {
        const transcript = event.results[event.results.length - 1][0].transcript;
        handleVoiceText(transcript);
      };

      recognition.onerror = (event) => {
        setListening(false);
        setStatusText("error");
        appendAssistant(`Voice input error: ${event.error}`);
      };

      recognition.onend = () => {
        setListening(false);
        if (voiceModeRef.current) {
          setTimeout(() => {
            try {
              recognition.start();
              setListening(true);
            } catch {
              // ignore
            }
          }, 400);
        }
      };

      recognitionRef.current = recognition;
    }

    setVoiceMode(true);
    setStatusText("listening");
    speak("Voice mode on. Say what you want to make.");

    try {
      recognitionRef.current.start();
      setListening(true);
    } catch {
      // ignore
    }
  }

  function stopVoiceMode() {
    setVoiceMode(false);
    setListening(false);

    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch {
        // ignore
      }
    }

    setStatusText("ready");
  }

  function clearPending() {
    if (actionTimerRef.current) clearTimeout(actionTimerRef.current);
    actionTimerRef.current = null;
    setPendingAction(null);
  }

  async function manualDispense(spice) {
    clearPending();
    setSelectedSpice(spice);
    setPendingAction({ kind: "spice", label: spice });
    setStatusText(`dispensing ${spice}`);
    setMessages((prev) => [...prev, { role: "assistant", content: `Dispensing ${spice}...` }]);

    actionTimerRef.current = setTimeout(async () => {
      try {
        const res = await fetch("/api/dispense", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ spice }),
        });

        const data = await res.json();
        if (!res.ok) {
          throw new Error(data?.error || "Dispense failed");
        }

        setMessages((prev) => [...prev, { role: "assistant", content: `${spice} dispensed.` }]);
        setStatusText(`${spice} sent`);
      } catch (error) {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: "Failed to send dispense command." },
        ]);
        setStatusText("error");
      } finally {
        clearPending();
      }
    }, 3000);
  }

  async function dispenseRecipe(card = recipe) {
    if (!card?.steps?.length) return;

    clearPending();
    setPendingAction({ kind: "recipe", label: card.title });
    setStatusText(`dispensing ${card.title}`);
    setMessages((prev) => [
      ...prev,
      { role: "assistant", content: `Dispensing recipe: ${card.title}...` },
    ]);

    try {
      const res = await fetch("/api/recipe/dispense", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ recipe: card }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data?.error || "Recipe dispense failed");
      }

      const approximateMs = Math.max(3000, card.steps.length * 3000);
      actionTimerRef.current = setTimeout(() => {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: `Recipe queued: ${card.steps.length} spice steps.` },
        ]);
        setStatusText("recipe sent");
        clearPending();
      }, approximateMs);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Failed to queue the recipe." },
      ]);
      setStatusText("error");
      clearPending();
    }
  }

  async function cancelPending() {
    if (pendingAction?.kind === "recipe") {
      try {
        await fetch("/api/recipe/cancel", { method: "POST" });
      } catch {
        // ignore cancel errors in demo mode
      }
    }

    clearPending();
    setStatusText("canceled");
    setMessages((prev) => [...prev, { role: "assistant", content: "Action canceled." }]);
  }

  function replaceRecipeStep(index, newSpice) {
    if (!recipe) return;

    const updated = {
      ...recipe,
      steps: recipe.steps.map((step, idx) =>
        idx === index ? { ...step, spice: newSpice } : step
      ),
    };

    setRecipe(updated);

    setMessages((prev) => [
      ...prev,
      {
        role: "assistant",
        content: `Updated step ${index + 1} to ${newSpice}.`,
      },
    ]);
  }

  function removeRecipeStep(index) {
    if (!recipe) return;

    const updated = {
      ...recipe,
      steps: recipe.steps.filter((_, idx) => idx !== index),
    };

    setRecipe(updated);
    setMessages((prev) => [
      ...prev,
      {
        role: "assistant",
        content: `Removed step ${index + 1}.`,
      },
    ]);
  }

  return (
    <div className="h-dvh overflow-hidden bg-[radial-gradient(circle_at_top,_rgba(34,211,238,0.18),_transparent_24%),radial-gradient(circle_at_bottom_right,_rgba(168,85,247,0.16),_transparent_20%),linear-gradient(180deg,_#000_0%,_#050816_36%,_#020617_100%)] text-white">
      <div className="mx-auto flex h-full max-w-7xl flex-col gap-4 p-4 sm:p-6 lg:p-8">
        <header className="rounded-[2.25rem] border border-white/10 bg-white/5 px-5 py-4 shadow-2xl backdrop-blur-xl">
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="flex h-14 w-14 items-center justify-center rounded-[1.5rem] border border-cyan-300/20 bg-cyan-300/10 shadow-[0_0_30px_rgba(34,211,238,0.16)]">
                <Bot className="h-6 w-6 text-cyan-100" />
              </div>
              <div>
                <div className="text-3xl font-black tracking-tight">Shroom Assistant</div>
                <div className="mt-1 text-sm text-slate-400">AI-guided seasoning carousel</div>
              </div>
            </div>

            <div className="rounded-full border border-white/10 bg-black/20 px-4 py-2 text-xs uppercase tracking-[0.22em] text-slate-300">
              {statusText}
            </div>
          </div>
        </header>

        <div className="grid flex-1 min-h-0 gap-4 lg:grid-cols-[1.2fr_0.9fr]">
          <section className="flex h-full min-h-0 flex-col overflow-hidden rounded-[2.5rem] border border-white/10 bg-white/5 shadow-2xl backdrop-blur-xl">
            <div className="border-b border-white/8 px-6 py-4">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-semibold tracking-tight">Assistant</h2>
                  <p className="mt-1 text-sm text-slate-400">Back-and-forth recipe building</p>
                </div>
                <div className="rounded-full border border-cyan-300/20 bg-cyan-300/10 px-3 py-1 text-xs uppercase tracking-[0.2em] text-cyan-200">
                  Live chat
                </div>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2 border-b border-white/8 px-6 py-3">
              <button
                type="button"
                onClick={voiceMode ? stopVoiceMode : startVoiceMode}
                className="inline-flex items-center gap-2 rounded-full border border-cyan-300/18 bg-cyan-300/10 px-3 py-2 text-xs font-medium text-cyan-100 transition hover:bg-cyan-300/16"
                aria-label={voiceMode ? "Stop voice mode" : "Start voice mode"}
              >
                <Mic className="h-4 w-4" />
                {listening ? "Listening…" : voiceMode ? "Stop voice mode" : "Voice mode"}
              </button>

              <button
                type="button"
                onClick={() => recipe && speakRecipe(recipe)}
                disabled={!recipe}
                className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-2 text-xs font-medium text-slate-200 transition hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-40"
                aria-label="Read current recipe aloud"
              >
                <Volume2 className="h-4 w-4" />
                Read recipe
              </button>

              <div className="text-xs text-slate-400">
                Say “read recipe,” “dispense recipe,” “repeat,” or “cancel.”
              </div>
            </div>

            <div
              ref={chatRef}
              role="log"
              aria-live="polite"
              aria-relevant="additions text"
              className="flex-1 min-h-0 overflow-y-auto px-6 py-5"
            >
              <div className="flex flex-col gap-4">
                {messages.map((m, idx) => (
                  <AssistantBubble key={idx} role={m.role}>
                    {m.content}
                  </AssistantBubble>
                ))}

                {recipe && (
                  <RecipeCard
                    recipe={recipe}
                    selectedSpice={selectedSpice}
                    onDispenseAll={() => dispenseRecipe(recipe)}
                    onReplaceStep={replaceRecipeStep}
                    onRemoveStep={removeRecipeStep}
                  />
                )}
              </div>
            </div>

            {pendingAction && (
              <div className="border-t border-white/8 px-6 py-4">
                <div className="rounded-[2rem] border border-amber-300/20 bg-amber-300/10 p-4">
                  <div className="text-xs uppercase tracking-[0.22em] text-amber-200">Action pending</div>
                  <div className="mt-2 text-lg font-semibold text-white">
                    {pendingAction.kind === "recipe" ? `Dispensing recipe: ${pendingAction.label}` : `Dispensing ${pendingAction.label}`}
                  </div>
                  <button
                    onClick={cancelPending}
                    type="button"
                    className="mt-4 inline-flex items-center gap-2 rounded-2xl border border-white/15 bg-white/5 px-4 py-3 text-sm font-medium text-white transition hover:bg-white/10"
                  >
                    <X className="h-4 w-4" />
                    Cancel
                  </button>
                </div>
              </div>
            )}

            <form onSubmit={handleSend} className="shrink-0 border-t border-white/8 px-6 py-5">
              <div className="flex items-end gap-3 rounded-[2rem] border border-white/10 bg-black/20 px-5 py-4">
                <div className="flex-1">
                  <label className="mb-2 block text-[11px] uppercase tracking-[0.25em] text-slate-400">
                    What are you cooking?
                  </label>
                  <textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        handleSend(e);
                      }
                    }}
                    rows={2}
                    placeholder="e.g. I want to make tacos"
                    className="w-full resize-none rounded-[1.5rem] border border-white/10 bg-slate-950/80 px-4 py-3 text-base text-white outline-none placeholder:text-slate-500 focus:border-cyan-300/40"
                  />
                </div>

                <button
                  type="submit"
                  className="inline-flex h-[54px] items-center gap-2 rounded-[1.4rem] bg-cyan-400 px-5 text-sm font-semibold text-slate-950 shadow-[0_0_24px_rgba(34,211,238,0.3)] transition hover:bg-cyan-300"
                >
                  <Send className="h-4 w-4" />
                  Send
                </button>
              </div>
            </form>
          </section>

          <aside className="flex h-full min-h-0 flex-col overflow-hidden rounded-[2.5rem] border border-white/10 bg-white/5 shadow-2xl backdrop-blur-xl">
            <div className="border-b border-white/8 px-6 py-4">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-semibold tracking-tight">Dispense spice</h2>
                  <p className="mt-1 text-sm text-slate-400">Choose a spice or use a recipe step</p>
                </div>
                <div className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs uppercase tracking-[0.2em] text-slate-300">
                  {selectedSpice}
                </div>
              </div>
            </div>

            <div className="flex-1 px-5 py-5">
              <div className="grid grid-cols-2 gap-3">
                {SPICES.map((spice) => (
                  <SpiceCard
                    key={spice.name}
                    spice={spice}
                    active={selectedSpice === spice.name}
                    onClick={setSelectedSpice}
                  />
                ))}
              </div>

              <div className="mt-4 rounded-[2rem] border border-white/10 bg-black/25 p-4">
                <div className="text-xs uppercase tracking-[0.22em] text-slate-400">Selected spice</div>
                <div className="mt-2 text-3xl font-black capitalize text-white">{selectedSpiceObj.name}</div>
                <p className="mt-2 text-sm text-slate-400">Ready to be dispensed by the carousel.</p>

                <button
                  type="button"
                  onClick={() => manualDispense(selectedSpiceObj.name)}
                  className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-[1.35rem] bg-white px-4 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-100"
                >
                  <CirclePlay className="h-4 w-4" />
                  Dispense selected spice
                </button>
              </div>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}
