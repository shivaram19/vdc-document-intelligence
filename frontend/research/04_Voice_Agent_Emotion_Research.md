# TRELO LABS RESEARCH BRIEF
## Voice Agent Emotion Fine-Tuning & Affective Computing (2025–2026)

**Prepared for:** Trelo Labs B2B Sales/Outreach Initiative  
**Focus:** Construction Industry Decision-Makers (Relationship-Driven Sales)  
**Date:** April 2026

---

## EXECUTIVE SUMMARY

The emotionally intelligent voice AI market has matured significantly in 2025–2026. What was experimental is now production-deployable. For B2B sales outreach—especially in relationship-driven industries like construction—voice agents can now modulate prosody (pitch, rhythm, stress, pacing) to convey empathy, urgency, authority, and warmth in real time. The leading platforms (Hume AI, ElevenLabs, OpenAI Realtime, Cartesia Sonic) offer APIs with sub-300ms latency, making real-time emotional adaptation feasible for live sales calls.[^1][^2]

**Critical insight for construction B2B:** Construction decision-makers (developers, project managers, procurement heads) operate in high-trust, long-cycle environments. Voice tone builds credibility faster than text. Research confirms that paralinguistic cues (volume variability, pitch contour, speech rate) drive persuasion by signaling confidence—and confidence is the primary mechanism by which voice tone converts to trust.[^3][^4]

---

## 1. STATE OF EMOTION-AWARE VOICE AI (2025–2026)

### 1.1 Hume AI — Empathic Voice Interface (EVI 3 / Octave TTS)
- **Product:** EVI 3 (launched 2025) + Octave 2 TTS
- **Core capability:** Real-time emotion detection from voice + expressive synthesis that adapts to conversational context automatically
- **Latency:** <300ms response time; under 200ms generation time for Octave 2[^5]
- **Pricing:**[^5]
  - Free: 10K chars/month + 5 min EVI
  - Starter: $3/mo (30K chars, 40 min)
  - Creator: $14/mo (140K chars, 200 min)
  - Pro: $70/mo (1M chars, 1,200 min)
  - Expression Measurement API: $0.0276/min video+audio, $0.00008/word text
- **Key differentiator:** Only platform combining emotion *detection* and *generation* natively. Octave TTS understands semantic context and adds appropriate emotion/pacing automatically.
- **Limitations:** 11 languages (expanding), word error rate 3.5% vs. industry-leading 2.83%[^6]

### 1.2 ElevenLabs — Emotional TTS & Speech-to-Speech
- **Product:** Eleven v3 (alpha), Speech-to-Speech (STS), Voice Design
- **Core capability:** Most expressive commercial TTS; emotion sliders; fine-grained prosody control; voice cloning from 6–30 seconds
- **Languages:** 29+ languages
- **Pricing:** Credit-based[^7]
  - Free: 10K chars/month
  - Starter: $5/mo (30K chars)
  - Creator: $22/mo (100K chars)
  - Pro: $99/mo (500K chars)
  - Business: $1,320/mo (custom)
- **Key differentiator:** Benchmark leader for voice realism (MOS 4.7–4.8/5).[^8] STS preserves original speaker's intonation/emotion while converting to cloned voice. "Emotion sliders" (+30% empathy, −20% urgency) available.
- **Limitations:** Emotion control is surface-level acoustic parameter adjustment, not deep contextual understanding. Latency varies by model (Flash ~75ms, Multilingual v3 slower).[^7]

### 1.3 OpenAI — GPT-Realtime & Native Audio Models
- **Product:** GPT-realtime-1.5 (GA August 2025), GPT-4o-mini-transcribe (Dec 2025)
- **Core capability:** End-to-end speech-to-speech without text intermediary; preserves emotional context, tone nuances, pauses, accents
- **Latency:** <500ms target; audio input $32/1M tokens, output $64/1M tokens (or ~$0.06/min input, $0.24/min output via time-based billing)[^9]
- **Key differentiator:** Native audio processing eliminates the "translation loss" of ASR→LLM→TTS pipelines. Custom Voices available for enterprise (contact sales).
- **Limitations:** Fewer voice-specific features than ElevenLabs; emotion control less granular.[^9]

### 1.4 Google — Gemini Audio, SoundStorm, AudioLM
- **Product:** Gemini 2.5 (native audio dialog), SoundStorm (parallel audio generation), AudioPaLM (speech-to-speech translation)
- **Core capability:** Multimodal text+audio understanding; neural audio codecs (SoundStream, EnCodec) for efficient tokenization
- **Status:** SoundStorm is research-grade (2023 paper, 30s audio in 0.5s on TPU); Gemini API available for speech generation[^10]
- **Key differentiator:** Massive infrastructure; 220+ voices in Cloud TTS; WaveNet prosody
- **Limitations:** SoundStorm not commercially available as standalone product; less emotional expressiveness than ElevenLabs/Hume[^10]

### 1.5 Meta — Audiobox
- **Product:** Audiobox (research demo, successor to Voicebox)
- **Status:** Research-only; no commercial licensing; most access requests denied
- **Assessment:** Not viable for production B2B use in 2026

### 1.6 Emerging Players
- **Cartesia Sonic 3:** State-space model TTS, sub-200ms time-to-first-audio, purpose-built for voice agents. Credit-based: Free (20K), Pro $5/mo (100K), Startup $49/mo (1.25M), Scale $299/mo (8M). 40+ languages.[^11]
- **Deepgram Aura-2:** Sub-200ms latency, STT+TTS unified. ~$0.08/min for voice agent API.[^12]
- **Resemble AI (Chatterbox-Turbo):** Open-source MIT license, sub-200ms, emotion exaggeration control, `[laugh]`/`[chuckle]` tags.[^13]
- **Dia2 (Nari Labs):** Open-source Apache 2.0, dialogue-first TTS, nonverbal tags `(laughs)`, `(sighs)`, streaming generation.[^14]

---

## 2. PROSODY MODULATION: HOW SYNTHETIC VOICES CONVEY EMOTION

### 2.1 Key Acoustic Parameters
Modern TTS systems control emotion through explicit manipulation of:[^15][^16]

| Parameter | Emotional Effect | Technical Implementation |
|-----------|-----------------|------------------------|
| **Pitch (F0)** | Higher = excitement, urgency, empathy; Lower = authority, calm, gravity | Direct pitch prediction (FastPitch[^17]), style embeddings, or diffusion guidance |
| **Speech rate / duration** | Faster = urgency, enthusiasm; Slower = authority, reassurance, sadness | Duration predictors (FastSpeech 2[^18]), token-level timing control |
| **Energy / loudness** | Louder + variable = confidence, persuasion; Softer = intimacy, empathy | Energy predictors, amplitude envelopes |
| **Pauses / rhythm** | Strategic pauses = authority, thoughtfulness; Reduced pauses = urgency | Punctuation-aware prosody models, SSML break tags |
| **Voice quality** | Breathy = warmth, intimacy; Tense = urgency, anger | Glottal source modeling, spectral tilt control |

### 2.2 Control Mechanisms in Production APIs
- **Natural language prompts:** "Say this with warm empathy" or "sound authoritative but approachable" (Hume Octave, InstructTTS[^19])
- **Style/emotion tags:** `[happy]`, `[urgent]`, `[calm]` (StyleTagging-TTS[^20], Chatterbox)
- **Emotion sliders:** Continuous control over intensity (ElevenLabs, Resemble AI)
- **Reference audio / prosody transfer:** Clone intonation from a sample (Microsoft Azure TTS, ElevenLabs STS)
- **SSML markup:** `<prosody pitch="+10%" rate="slow">` (Google, Azure, Amazon Polly)
- **Nonverbal tags:** `(laughs)`, `(sighs)`, `(gasps)` — Dia2, Chatterbox-Turbo[^14]

### 2.3 What the Research Says
- **Confidence mediation:** Speakers who increase volume and volume variability during persuasion attempts are perceived as more confident, which enhances persuasion.[^3]
- **Paralinguistic > linguistic:** Paralinguistic persuasion attempts can be effective even when linguistic persuasion is not. Listeners detect the attempt but are still persuaded because it signals conviction.[^3]
- **Falling intonation signals confidence:** Low pitch/fast speech (vs. high pitch/slow speech) is perceived as more confident and can validate listeners' positive thoughts under high-elaboration conditions, enhancing persuasion via metacognitive validation.[^4]

---

## 3. VOICE INTERACTION PSYCHOLOGY: TRUST, PERSUASION, "HOOKING"

### 3.1 The Science of Vocal Persuasion
Research from Wharton (Van Zant & Berger) and Universidad Autónoma de Madrid (Briñol et al.) establishes:[^3][^4]

1. **Confidence is the mediator:** Vocal cues don't persuade directly—they persuade by making the speaker seem more confident, which implies they hold more extreme/consistent attitudes.[^3]
2. **Specific effective cues:**
   - **Increased volume** (louder speech)
   - **Volume variability** (dynamic range, not monotone)
   - **Faster speech rate** (within limits—too fast reduces comprehension)
   - **Fewer pauses / shorter latencies** (signals preparedness and certainty)
3. **Low registers** convey authority, gravitas, calm reassurance[^4]
4. **High registers** convey enthusiasm, urgency, vulnerability/empathy

### 3.2 Implications for B2B Construction Sales
Construction decision-makers are:
- **Risk-averse:** They respond to **authority** (lower pitch, measured pace, strategic pauses) and **warmth** (slight breathiness, moderate pitch variability)[^3][^4]
- **Relationship-driven:** First impressions form within milliseconds of voice contact.[^21] Vocal confidence signals competence.
- **Time-constrained:** Urgency must feel genuine, not salesy. Moderate rate increase + slightly elevated pitch on key value propositions.

**Recommended opening structure for construction DM voice agents:**
- **0–3 seconds:** Warm, confident greeting (mid-low register, moderate volume)
- **3–8 seconds:** Value proposition with slight rate increase and volume emphasis on outcome words ("reduce delays," "cut material waste")
- **8–15 seconds:** Strategic pause + empathetic acknowledgment of pain point (slightly softer, slower)

> *Note: The above timing structure is a recommended synthesis of vocal persuasion research rather than a tested formula.*

---

## 4. KEY PAPERS & CONFERENCES (2025–2026)

### 4.1 Notable Recent Papers
| Paper | Authors | Venue | Contribution | URL |
|-------|---------|-------|------------|-----|
| [**UDDETTS: Unifying Discrete and Dimensional Emotions for Controllable Emotional TTS**](https://arxiv.org/abs/2505.10599) | Liu et al. | arXiv 2025 | Bridges categorical and dimensional emotion models | [arXiv](https://arxiv.org/abs/2505.10599) |
| [**Llasa: Scaling Train-Time and Inference-Time Compute for Llama-based Speech Synthesis**](https://arxiv.org/abs/2502.04128) | Ye et al. | arXiv 2025 | LLM-initialized TTS with style control | [arXiv](https://arxiv.org/abs/2502.04128) |
| [**DrawSpeech: Expressive Speech Synthesis Using Prosodic Sketches**](https://arxiv.org/abs/2501.04256) | Chen et al. | ICASSP 2025 | Prosodic sketch-based control | [arXiv](https://arxiv.org/abs/2501.04256) |
| [**PROEMO: Prompt-Driven TTS Based on Emotion and Intensity Control**](https://arxiv.org/abs/2501.06276) | Zhang et al. | arXiv 2025 | Natural language emotion prompts | [arXiv](https://arxiv.org/abs/2501.06276) |
| [**EmoKnob: Enhance Voice Cloning with Fine-Grained Emotion Control**](https://arxiv.org/abs/2410.00316) | Chen, Hirschberg | EMNLP 2024 | Scaled emotion difference vectors | [arXiv](https://arxiv.org/abs/2410.00316) |
| [**Towards Controllable Speech Synthesis in the Era of LLMs: A Survey**](https://arxiv.org/abs/2412.06602) | Xie et al. | arXiv 2025 | Comprehensive survey of control strategies | [arXiv](https://arxiv.org/abs/2412.06602) |
| [**Segment-Aware Conditioning for Training-Free Intra-Utterance Emotion Control**](https://arxiv.org/abs/2601.03170) | Liang et al. | arXiv 2026 | Training-free emotion interpolation | [arXiv](https://arxiv.org/abs/2601.03170) |
| **Hierarchical Semantic-Acoustic Modeling via Semi-Discrete Residual Representations** | Zhou et al. | ICLR 2026 | Expressive end-to-end synthesis | ICLR 2026 |

### 4.2 Key Conferences
- **ICASSP 2025 / 2026:** Emotional TTS, prosody control, voice conversion
- **Interspeech 2025 / 2026:** Speech emotion recognition, conversational synthesis, multimodal emotion
- **NeurIPS 2025:** Audio Imagination Workshop, generative AI for speech evaluation
- **EMNLP 2025:** LLM-based controllable TTS, emotion captioning, multimodal sentiment
- **ACL 2025 / NAACL 2025:** Emotion recognition with vocal nuances, prompt-based prosody

---

## 5. FINE-TUNING VOICE AGENTS FOR EMOTIONAL REGISTERS

### 5.1 Four Core Registers for B2B Sales

| Register | Target Context | Vocal Profile | Prompt/Control Strategy |
|----------|---------------|---------------|------------------------|
| **Empathy** | Acknowledging pain points, objections | Slightly elevated pitch, moderate variability, softer volume, slower pace with gentle rises | "Say this with genuine understanding, like you're hearing their frustration for the first time" |
| **Urgency** | Limited-time offers, scheduling pressure | Faster rate, sharper pitch rises on key words, increased volume on action items, minimal pauses | "Convey this with quiet urgency—not pushy, but important" |
| **Authority** | Credibility statements, industry expertise | Lower register, slower measured pace, strategic pauses, steady volume, reduced pitch variability | "Deliver this with calm authority, like a trusted advisor" |
| **Warmth** | Rapport building, relationship initiation | Moderate pitch, breathy voice quality, gentle volume swells, conversational rate | "Sound warm and approachable, like catching up with a colleague" |

### 5.2 Fine-Tuning Approaches

**A. Prompt-Based Control (Fastest, Good Enough for Most)**
- Use natural language prompts with Hume Octave or ElevenLabs v3
- A/B test prompt variations against conversion metrics
- Cost: Minimal; requires only copywriting iteration

**B. Reference Audio / Prosody Transfer (Higher Fidelity)**
- Record human sales performers delivering each register
- Use as reference audio for ElevenLabs STS or Azure TTS voice conversion
- Cost: Moderate; requires voice talent and sample curation

**C. Style Embedding Fine-Tuning (Most Control)**
- Train Global Style Tokens (GST) or emotion embeddings on labeled sales call datasets
- Requires technical ML infrastructure (PyTorch/TensorFlow)
- Cost: High; 3–6 months engineering effort

**D. Inference-Time Emotion Steering (Emerging)**
- EmoSteer-TTS style: manipulate token-level activations in pretrained diffusion models[^22]
- No retraining required; interpolate between emotion vectors in real time
- Cost: Medium; requires research engineering expertise

---

## 6. TECHNICAL ARCHITECTURES

### 6.1 Recommended Stack for Emotionally Intelligent B2B Voice Agent

```
┌─────────────────────────────────────────────────────────────┐
│  INPUT: Caller audio stream                                  │
├─────────────────────────────────────────────────────────────┤
│  LAYER 1: Real-Time Emotion Detection                        │
│  • Acoustic features (prosody, voice quality, temporal)     │
│  • NLP sentiment on ASR transcript                          │
│  • Multimodal fusion (confidence >80% → auto-adapt)         │
│  • Latency target: <150ms                                    │
├─────────────────────────────────────────────────────────────┤
│  LAYER 2: LLM Reasoning + Emotional Context Injection        │
│  • System prompt encodes detected emotion + target register │
│  • Generate response text + emotional direction tag           │
│  • Fast model: GPT-4o-mini / Gemini Flash / Llama 3 70B     │
│  • Latency target: <400ms                                    │
├─────────────────────────────────────────────────────────────┤
│  LAYER 3: Emotionally Adaptive TTS                           │
│  • Hume Octave (context-aware) OR                           │
│  • ElevenLabs v3 + emotion prompt OR                        │
│  • Cartesia Sonic + speed/pitch/emotion params              │
│  • Latency target: <200ms                                    │
├─────────────────────────────────────────────────────────────┤
│  OUTPUT: Emotionally adapted voice response                  │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Latency Budget for Natural Conversation
- **Total end-to-end:** <800ms (ideally 500–700ms)
- **Detection:** 50–150ms
- **LLM reasoning:** 200–400ms
- **TTS generation:** 75–300ms
- **Telephony overhead:** 50–100ms

> *Note: Latency targets are industry benchmarks derived from voice AI platform documentation and conversational AI best-practice guides.*

### 6.3 Open-Source Options for Custom Development
- **Dia2:** Dialogue TTS with nonverbal tags, streaming, Apache 2.0[^14]
- **Chatterbox-Turbo:** Sub-200ms, emotion exaggeration, MIT license[^13]
- **XTTS-v2:** Voice cloning + emotion transfer, 17 languages (non-commercial license)
- **ChatTTS:** Conversational TTS, English/Chinese, token-level control

---

## 7. VOICE AGENTS FOR B2B SALES/OUTREACH: CONSTRUCTION INDUSTRY

### 7.1 Why Construction?
Construction B2B sales are notoriously difficult:
- **Long sales cycles:** The average B2B sales cycle has stretched to 6.5 months, up from 4.9 months in 2019.[^23] Real estate and construction leads average 147-day sales cycles.[^24]
- **Complex DMUs:** The typical B2B purchase involves 6–10 stakeholders, with newer studies pushing that average to 10–11.[^23]
- **Relationship-driven:** Decisions hinge on trust and prior performance
- **Fragmented market:** Thousands of SMBs + few enterprise giants

### 7.2 Where Voice Agents Fit
- **Initial outreach/cold calling:** AI-personalized calls achieve **36% higher meeting conversion** than generic outreach.[^25]
- **Qualification:** Automated systems can handle thousands of simultaneous conversations, where human SDRs complete 50–80 calls per day.[^25]
- **Follow-up persistence:** Most deals require **5–12 touchpoints** to close for warm leads, and 20–50 for cold leads.[^26]
- **Appointment setting:** Consistent, always-available scheduling

### 7.3 Voice-Specific Advantages for Construction DMs
- **Trust signaling:** A confident, warm voice establishes credibility faster than email[^3]
- **Handling objections in real time:** Emotional detection flags frustration → agent switches to empathy register
- **Regional accent matching:** Clone voices with local accents to increase familiarity (ElevenLabs, XTTS-v2 support this)

### 7.4 Expected Performance Benchmarks (2026)
- **AI personalized calls:** +36% meeting conversion vs generic (Outreach 2025 dataset)[^25]
- **Cost per lead:** 42% reduction vs human SDRs alone (industry case studies)[^25]
- **Response latency:** 500–800ms on leading platforms
- **First-call resolution:** Industry targets exceed 80% for appointment-setting use cases; mature deployments regularly achieve 65–75% containment.[^27]

---

## 8. ETHICAL & REGULATORY CONSIDERATIONS

### 8.1 U.S. Federal Requirements

**FCC — TCPA & AI Voice (Active)**
- **Feb 2024 Declaratory Ruling:** AI-generated voices = "artificial or prerecorded voice" under TCPA[^28]
- **Consent required:** Express written consent for outbound AI voice calls
- **Sept 2024 NPRM (pending final rule):**
  - Consent disclosure: Must disclose AI-generated content when obtaining consent
  - **In-call disclosure:** Must clearly identify as AI-generated at start of call
  - Opt-out mechanism: Automated, interactive, within 2 seconds of initial message
- **Penalties:** Up to $500–$1,500 per violation; state AG enforcement[^28]

**FTC — Transparency & Deception (Evolving)**
- **March 11, 2026 deadline:** FTC must publish AI policy statement per Trump EO[^29]
- **Current enforcement:** Section 5 FTC Act prohibits deceptive practices; AI impersonation of humans/businesses is flatly prohibited
- **Expected phases:** Warning letters (Q2 2026) → Consent orders (Q3–Q4) → Full enforcement (2027+)
- **Penalties:** Up to $50,120 per violation (16 C.F.R. § 1.98, 2025 adjustment)[^30]

### 8.2 State Laws
- **Tennessee ELVIS Act (2024):** Prohibits unauthorized commercial voice likeness; civil damages. Signed March 21, 2024; effective July 1, 2024.[^31]
- **California:** AB 2602 (digital replica contracts, effective Jan 1, 2025[^32]); AB 1836 (deceased personality rights, effective Jan 1, 2026[^33])
- **New York:** Digital Replica Contracts Act (effective Jan 1, 2025) — voids contract terms permitting a digital replica to substitute for a performer's work unless the intended uses are reasonably specific and the performer has legal or union representation.[^34]
- **Utah UAIPA (2024):** AI disclosure requirements for consumer-facing AI

### 8.3 International
- **EU AI Act (Regulation EU 2024/1689):** Entered force Aug 1, 2024. Article 50 transparency obligations — including chatbot disclosure and deepfake labeling — become enforceable Aug 2, 2026.[^35]
- **China Deep Synthesis Regulation (2023):** Watermarks on AI-generated voice/face content[^36]
- **Brazil LGPD Amendment (proposed):** Voiceprints as sensitive personal data

### 8.4 Best Practices for B2B Voice Agents
1. **Upfront disclosure:** "Hello, I'm an AI assistant calling on behalf of [Company]" — first 3 seconds
2. **Explicit consent:** Obtain TCPA-compliant written consent before outbound AI calls
3. **Opt-out:** "Press 0 or say 'operator' at any time to speak with a human"
4. **No impersonation:** Never clone a real person's voice without explicit permission
5. **Emotional boundaries:** Use emotion detection for service/empathy, not manipulation. Avoid exploiting detected distress to pressure decisions
6. **Audit trails:** Log all AI decisions, disclosures, and consent records
7. **Bias auditing:** Test emotion detection accuracy across accents, demographics, and emotional expression styles

### 8.5 Construction Industry Nuance
Construction is a regulated industry with high liability sensitivity. Decision-makers may react negatively to "trick" AI. **Transparency builds trust.** Position the AI as a "scheduling assistant" that ensures they get connected to the right human expert quickly.

---

## 9. BEST PLATFORMS/TOOLS TO BUILD TODAY

### 9.1 For Rapid Deployment (No-Code/Low-Code)

| Platform | Best For | Pricing | Emotion Features |
|----------|----------|---------|-----------------|
| **Retell AI** | Fastest path to production phone agent | $0.07–$0.31/min | Managed pipeline; brings own TTS (ElevenLabs/Hume) |
| **Vapi** | Developer flexibility, multi-provider | $0.05/min platform + provider costs | Integrates Hume Octave at low latency |
| **Bland AI** | High-volume outbound | $0.09–$0.12/min; $299–$499/mo tiers | Voice cloning included; conversational pathways |
| **Synthflow** | No-code SMB deployment | $0.08–$0.13/min | SOC2/HIPAA/GDPR compliant |
| **Astra Voice 2.0** | WhatsApp + voice unified | $99–$399/mo | Fully no-code |

### 9.2 For Best Emotional Intelligence

| Platform | Best For | Pricing | Key Feature |
|----------|----------|---------|-------------|
| **Hume AI EVI 3 + Octave 2** | Emotion detection + generation | $3–$500/mo | Only native empathic voice interface; auto-adapts tone[^5] |
| **ElevenLabs v3** | Highest voice realism | $5–$1,320/mo | Emotion sliders, STS, 29 languages, MOS 4.7–4.8[^8] |
| **Cartesia Sonic 3** | Ultra-low latency agents | $5–$299/mo credit-based | Sub-200ms TTFB, pitch/speed/emotion control, 40+ languages[^11] |
| **OpenAI Realtime API** | End-to-end speech understanding | $0.06/min in, $0.24/min out | Native audio, preserves emotion context, Custom Voices[^9] |

### 9.3 For Emotion Detection Only

| Platform | Accuracy | Pricing | Best For |
|----------|----------|---------|----------|
| **Intervo.ai** | 95%+ | Enterprise custom | Real-time emotional analysis, predictive sentiment |
| **Hume Expression Measurement** | High | $0.0276/min video+audio | Multimodal (voice+face+text), granular emotion dimensions[^5] |
| **Balto** | Real-time coaching | Enterprise | Live agent coaching, sentiment alerts |
| **Dialpad AI** | Live transcription + sentiment | Per-seat | Call center integration |

### 9.4 Recommended Stack for Trelo Labs (Construction B2B)

**Phase 1 — MVP (Weeks 1–4):**
- **Voice agent platform:** Vapi or Retell AI (fastest deployment)
- **TTS:** Hume Octave 2 (emotion-aware) OR ElevenLabs v3 (quality)
- **STT:** Deepgram Nova-2 or OpenAI Whisper (lowest WER)
- **LLM:** GPT-4o-mini or Claude 3.5 Haiku (fast, cost-effective)
- **Emotion detection:** Hume Expression Measurement API
- **Telephony:** Twilio (flexible, global numbers)

**Phase 2 — Scale (Months 2–6):**
- Migrate to **custom stack** on Vapi for cost optimization
- A/B test emotion registers using ElevenLabs STS with reference audio
- Implement **prosody transfer** from top-performing human sales calls
- Add **real-time emotion adaptation loop:** detect caller emotion → adjust TTS prompt

**Phase 3 — Differentiation (Months 6–12):**
- Fine-tune custom voice on construction-specific vocabulary
- Explore **OpenAI Custom Voices** or **Cartesia professional voice cloning**
- Implement **inference-time emotion steering** (research-grade)[^22]
- Build proprietary emotion→conversion analytics

---

## 10. EMOTION DETECTION ↔ EMOTION GENERATION: THE CLOSED LOOP

### 10.1 How the Pairing Works

**Detection side:**
- **Acoustic:** Prosody (pitch, rate, volume), voice quality (jitter, shimmer, HNR), temporal dynamics
- **Linguistic:** Sentiment classification (85–92% accuracy on benchmark datasets), emotion classification (75–85%), context-aware models (+15–20% accuracy)[^38]
- **Fusion:** Multimodal fusion improves accuracy 10–15 percentage points over single modality[^38]

**Generation side:**
- TTS engine receives: `(response_text, target_emotion_register, intensity_scalar)`
- Emotion register maps to: `(pitch_offset, rate_multiplier, energy_target, pause_profile)`

### 10.2 Real-Time Adaptation Logic

```
IF caller_emotion == "frustrated" AND confidence > 0.8:
    target_register = "empathy"
    intensity = 0.7
    rate = 0.9x (slightly slower)
    volume = 0.85x (softer)

ELIF caller_emotion == "rushed/dismissive":
    target_register = "authority"
    intensity = 0.6
    rate = 1.1x (slightly faster)
    pitch = -5% (lower)

ELIF caller_emotion == "engaged/curious":
    target_register = "warmth"
    intensity = 0.8
    rate = 1.0x
    pitch_variability = +15%
```

### 10.3 Business Impact
- **Escalation reduction:** Cisco Webex AI Agent reduced call escalations by 85% for one large equipment rental customer, primarily by handling more issues autonomously through better escalation design.[^39]
- **Call abandonment:** Companies using AI voice emotion detection report 15–25% decreases in call abandonment rates by catching frustration early.[^40]
- **Compliance:** Emotion detection can flag distressed callers for mandatory human handoff

---

## ACTIONABLE RECOMMENDATIONS

### Immediate (This Week)
1. **Sign up for free tiers:** Hume AI (Creator plan, $14), ElevenLabs (Starter, $5), Vapi ($10 credits), Retell ($10 credits)
2. **Build a 3-minute demo:** Script a construction sales intro; generate versions in empathy, authority, urgency, and warmth registers
3. **A/B test with 5–10 construction contacts:** Ask for subjective feedback on which voice feels most trustworthy

### Short-Term (This Month)
4. **Choose primary stack:** For fastest time-to-value → **Retell AI + Hume Octave**. For maximum quality control → **Vapi + ElevenLabs v3 + Hume detection**
5. **Draft compliance protocol:** Include upfront AI disclosure, TCPA consent language, opt-out mechanism
6. **Record reference audio:** Have your best human sales rep record 10–15 sample lines in each register for prosody transfer

### Medium-Term (This Quarter)
7. **Deploy pilot campaign:** 500 calls to construction decision-makers; measure meeting conversion vs human SDR baseline
8. **Implement real-time emotion loop:** Connect Hume detection API to TTS prompt engineering
9. **Build analytics dashboard:** Track emotion detection confidence, register usage, and conversion correlation

### Long-Term (6–12 Months)
10. **Invest in custom voice cloning:** Create a proprietary "Trelo Labs voice" optimized for construction industry trust signals
11. **Explore open-source models:** Evaluate Dia2 or Chatterbox for on-premise deployment (data privacy for enterprise clients)
12. **Publish ethical framework:** Position Trelo Labs as a leader in transparent, consent-based AI voice sales

---

## APPENDIX: COST MODELS (ESTIMATED MONTHLY AT SCALE)

**Scenario: 10,000 minutes/month of AI voice calls**

| Component | Platform | Cost |
|-----------|----------|------|
| Voice agent platform | Vapi | $500 (platform) |
| TTS | Hume Octave 2 | ~$200–$400 |
| STT | Deepgram Nova-2 | ~$300 |
| LLM | GPT-4o-mini | ~$400 |
| Telephony | Twilio | ~$300 |
| Emotion detection | Hume Expression | ~$800 |
| **Total** | | **~$2,500–$2,700/mo** |
| **Effective rate** | | **~$0.25–$0.27/min** |

**Comparison:** Human SDR at $60K/year + overhead = ~$7,500/mo handling ~2,000 calls. AI agent handles 5x volume at 1/3 cost with 24/7 availability.

---

## REFERENCES

[^1]: Hume AI. (2025). *Announcing EVI 3 API: The most customizable speech-to-speech model*. [hume.ai](https://www.hume.ai/blog/announcing-evi-3-api)

[^2]: Van Zant, A. B., & Berger, J. (2020). How the voice persuades. *Journal of Personality and Social Psychology*, 118(4), 661–682. [DOI](https://doi.org/10.1037/pspi0000193)

[^3]: Van Zant, A. B., & Berger, J. (2020). How the voice persuades. *Journal of Personality and Social Psychology*, 118(4), 661–682. [DOI](https://doi.org/10.1037/pspi0000193)

[^4]: Vaughan-Johnston, T. I., Guyer, J. J., Fabrigar, L. R., Lamprinakos, G., & Briñol, P. (2024). Falling vocal intonation signals speaker confidence and enhances persuasion by increasing elaboration. *Personality and Social Psychology Bulletin*. [pablobrinol.com](https://pablobrinol.com/wp-content/uploads/2025/03/2024-PSPB-low-pitch-of-the-source-increases-elb-of-the-recipient.pdf)

[^5]: Hume AI. (2025). *Pricing*. [hume.ai](https://www.hume.ai/pricing)

[^6]: Max Productive AI. (2026). *Hume AI — Emotional Voice Generator Guide*. [max-productive.ai](https://max-productive.ai/ai-tools/hume-ai/)

[^7]: ElevenLabs. (2026). *Pricing & Plans*. [elevenlabs.io](https://elevenlabs.io/pricing)

[^8]: CodeSOTA. (2026). *Text-to-Speech Benchmarks*. [codesota.com](https://www.codesota.com/text-to-speech)

[^9]: OpenAI. (2025). *Realtime API*. [platform.openai.com](https://platform.openai.com/docs/guides/realtime)

[^10]: Google DeepMind. (2023). *SoundStorm: Efficient Parallel Audio Generation*. [deepmind.google](https://deepmind.google/research/publications/80756/)

[^11]: Cartesia. (2026). *Sonic*. [cartesia.ai](https://www.cartesia.ai/sonic)

[^12]: Deepgram. (2026). *Aura-2*. [deepgram.com](https://deepgram.com/product/aura-2)

[^13]: Resemble AI. (2026). *Chatterbox-Turbo*. [resemble.ai](https://www.resemble.ai/chatterbox-turbo/)

[^14]: Nari Labs. (2026). *Dia2*. [nari-labs/dia](https://github.com/nari-labs/dia)

[^15]: Guyer, J. J., Briñol, P., Vaughan-Johnston, T. I., Fabrigar, L. R., Moreno, L., & Petty, R. E. (2021). Paralinguistic features communicated through voice can affect appraisals of confidence and evaluative judgments. *Journal of Nonverbal Behavior*, 45, 399–425. [DOI](https://doi.org/10.1007/s10919-021-00374-2)

[^16]: FastPitch / FastSpeech 2 architectural parameters are standard in neural TTS literature. See Ren et al. (2019) *FastSpeech* and Łącki et al. (2021) *FastPitch*.

[^17]: Łącki, K., Lancucki, A., Yanguas-Gil, A., Hackett, P., Strom, N., & Miller, S. (2021). FastPitch: Parallel text-to-speech with pitch prediction. *IEEE ICASSP*.

[^18]: Ren, Y., Hu, C., Tan, X., Qin, T., Zhao, S., Zhao, Z., & Liu, T.-Y. (2019). FastSpeech 2: Fast and high-quality end-to-end text to speech. *NeurIPS 2020*.

[^19]: Yang, D., et al. (2023). InstructTTS: Modelling expressive TTS in discrete latent space with natural language style prompt. *arXiv:2301.13662*.

[^20]: StyleTagging-TTS references are cited in Xie et al. (2025) survey. See Xie, T., et al. (2025). Towards controllable speech synthesis in the era of large language models: A survey. *arXiv:2412.06602*.

[^21]: Willis, J., & Todorov, A. (2006). First impressions: Making up your mind after a 100-ms exposure to a face. *Psychological Science*, 17(7), 592–598. [DOI](https://doi.org/10.1111/j.1467-9280.2006.01750.x)

[^22]: Xie, T., Rong, Y., Zhang, P., Wang, W., & Liu, L. (2025). EmoSteer-TTS: Fine-grained and training-free emotion-controllable text-to-speech via activation steering. *arXiv:2508.03543*.

[^23]: Gradient Works. (2025). *2025 B2B sales performance benchmarks*. [gradient.works](https://www.gradient.works/blog/2025-b2b-sales-performance-benchmarks)

[^24]: Ritner Digital. (2026). *Which industries have the longest marketing cycles*. [ritnerdigital.com](https://www.ritnerdigital.com/blog/which-industries-have-the-longest-marketing-cycles-and-what-does-the-data-actually-say)

[^25]: MarketsandMarkets / Prospeo. (2026). *Voice AI Agents in Cold Calling: What Actually Works in 2026*. [marketsandmarkets.com](https://www.marketsandmarkets.com/AI-sales/voice-ai-can-agents-successfully-cold-call); [prospeo.io](https://prospeo.io/s/conversational-ai-for-sales)

[^26]: Kondo. (2025). *B2B Sales Benchmarks 2025*. [trykondo.com](https://www.trykondo.com/blog/b2b-sales-benchmarks-2025); Email Tool Tester. (2025). *How many touchpoints before a sale in 2026?* [emailtooltester.com](https://www.emailtooltester.com/en/blog/how-many-touchpoints-before-a-sale/)

[^27]: VoiceInfra.ai. (2025). *Voice AI Prompt Engineering: Complete Technical Guide*. [voiceinfra.ai](https://voiceinfra.ai/blog/voice-ai-prompt-engineering-complete-guide); Trillet.ai. (2026). *Voice AI Contact Center KPIs*. [trillet.ai](https://trillet.ai/blogs/voice-ai-contact-center-kpis)

[^28]: FCC. (2024). *Declaratory Ruling and Order*, CG Docket No. 23-362 (Feb. 8, 2024). [docs.fcc.gov](https://docs.fcc.gov/public/attachments/FCC-24-17A1.pdf); Wiley Law. (2024). *FCC Declares AI-Generated Voices in Robocalls Illegal*. [wiley.law](https://www.wiley.law/alert-fcc-declares-ai-generated-voices-in-robocalls-illegal)

[^29]: Baker Donelson. (2026). *Emerging Federal AI Policy: What To Know and How To Prepare*. [bakerdonelson.com](https://www.bakerdonelson.com/emerging-federal-ai-policy-what-to-know-and-how-to-prepare)

[^30]: FTC Authority. (2026). *FTC Oversight of Artificial Intelligence and Algorithms*. [ftcauthority.com](https://ftcauthority.com/ftc-artificial-intelligence-policy); 16 C.F.R. § 1.98 (2025 adjustment).

[^31]: Tennessee General Assembly. (2024). *Ensuring Likeness Voice and Image Security (ELVIS) Act*, Pub. Ch. 702 (signed March 21, 2024; effective July 1, 2024). [publications.tnsosfiles.com](https://publications.tnsosfiles.com/acts/113/pub/pc0702.pdf)

[^32]: California Legislature. (2024). AB 2602 — Digital replicas: contracts (signed Sept. 28, 2024; effective Jan. 1, 2025). [leginfo.legislature.ca.gov](https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=202320240AB2602)

[^33]: California Legislature. (2024). AB 1836 — Digital replicas: deceased personality (signed Sept. 28, 2024; effective Jan. 1, 2026). [leginfo.legislature.ca.gov](https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=202320240AB1836)

[^34]: New York State Assembly. (2024). Digital Replica Contracts Act (effective Jan. 1, 2025). See analysis at [practiceguides.chambers.com](https://practiceguides.chambers.com/practice-guides/comparison/1012/17371/27168-27169-27170-27171-27172-27173-27174-27175-27176-27177)

[^35]: European Parliament. (2024). Regulation (EU) 2024/1689 — Artificial Intelligence Act (entered force Aug. 1, 2024). Article 50 transparency obligations applicable Aug. 2, 2026. [eur-lex.europa.eu](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=OJ:L_202401689)

[^36]: Cyberspace Administration of China. (2023). *Provisions on the Administration of Deep Synthesis Internet Information Services* (effective Jan. 10, 2023). [cac.gov.cn](http://www.cac.gov.cn/2022-12/11/c_1672221949354811.htm)

[^38]: Academic synthesis drawn from: Kumar et al. (2025) *Multimodal emotion detection using advanced deep learning* (97% accuracy with text+image+speech); EmoChat (2019) * Bringing multimodal emotion detection to mobile conversation* (76.25% polarity, 51.64% category); and ParallelNet (2022) *Interpretable multimodal emotion recognition* (89.68% sentiment, 83.29% emotion).

[^39]: Bucher + Suter. (2026). *Escalation Design: Why AI Fails at the Handoff*. [bucher-suter.com](https://www.bucher-suter.com/escalation-design-why-ai-fails-at-the-handoff-not-the-automation/)

[^40]: Dialzara. (2025). *How Do Voice Agents Detect Customer Emotions and Sentiment?* [dialzara.com](https://dialzara.com/blog/how-ai-detects-customer-emotions-in-calls)

---

*End of Research Brief — Cited Edition*
