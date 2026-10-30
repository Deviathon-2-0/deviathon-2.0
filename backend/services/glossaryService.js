/**
 * IMAIRA+ Glossary Service
 * 
 * Provides efficient technical term matching and correction candidate generation.
 * Designed to load the supplied technical glossary when it becomes available.
 * Currently uses a small test fixture for development.
 * 
 * IMPORTANT: This service generates CANDIDATES — it never silently rewrites transcripts.
 */
const fs = require("fs");
const path = require("path");

// Default glossary path — override via GLOSSARY_PATH env variable
const GLOSSARY_PATH = process.env.GLOSSARY_PATH ||
  path.join(__dirname, "../data/glossary_test_fixture.json");

let glossaryData = null;
let variantMap = null; // Maps lowercase variant → { canonical, variant }

/**
 * Load and index the glossary for efficient matching.
 * Safe to call multiple times — will only load once unless force=true.
 */
function loadGlossary(force = false) {
  if (glossaryData && !force) return glossaryData;

  try {
    if (!fs.existsSync(GLOSSARY_PATH)) {
      console.warn(`[Glossary] Glossary file not found at ${GLOSSARY_PATH}. Running without glossary.`);
      glossaryData = { terms: [] };
      variantMap = new Map();
      return glossaryData;
    }

    const raw = fs.readFileSync(GLOSSARY_PATH, "utf-8");
    glossaryData = JSON.parse(raw);

    // Build a variant → canonical lookup map
    variantMap = new Map();
    for (const entry of glossaryData.terms || []) {
      const canonical = entry.canonical;
      for (const variant of entry.variants || []) {
        const key = variant.toLowerCase().trim();
        if (key.length >= 2) { // Skip single-character variants
          variantMap.set(key, { canonical, variant });
        }
      }
    }

    console.log(`[Glossary] Loaded ${glossaryData.terms.length} terms with ${variantMap.size} variants from ${GLOSSARY_PATH}`);
    return glossaryData;
  } catch (err) {
    console.error(`[Glossary] Failed to load glossary:`, err.message);
    glossaryData = { terms: [] };
    variantMap = new Map();
    return glossaryData;
  }
}

/**
 * Generate correction candidates for a transcript.
 * 
 * @param {string} transcript - The original transcription text
 * @param {string} [questionContext] - The interview question (for context scoring)
 * @returns {Array} correction candidates, each with:
 *   - original: the word/phrase found in transcript
 *   - suggested: the canonical technical term
 *   - confidence: "high" | "medium" | "low"
 *   - context: surrounding words
 *   - position: { start, end } character offsets
 */
function generateCorrectionCandidates(transcript, questionContext = "") {
  if (!transcript || typeof transcript !== "string") return [];

  // Ensure glossary is loaded
  loadGlossary();
  if (!variantMap || variantMap.size === 0) return [];

  const candidates = [];
  const lowerTranscript = transcript.toLowerCase();
  const lowerQuestion = questionContext.toLowerCase();
  const seen = new Set(); // Deduplicate

  for (const [variantKey, { canonical, variant }] of variantMap) {
    // Skip if the variant IS the canonical form (exact match = not a correction)
    if (variantKey === canonical.toLowerCase()) continue;

    // Find all occurrences of this variant in the transcript
    let searchPos = 0;
    while (searchPos < lowerTranscript.length) {
      const idx = lowerTranscript.indexOf(variantKey, searchPos);
      if (idx === -1) break;

      // Check word boundaries to avoid matching inside longer words
      const charBefore = idx > 0 ? lowerTranscript[idx - 1] : " ";
      const charAfter = idx + variantKey.length < lowerTranscript.length
        ? lowerTranscript[idx + variantKey.length]
        : " ";

      const isBoundaryBefore = /[\s,.;:!?'"()\-\/]/.test(charBefore);
      const isBoundaryAfter = /[\s,.;:!?'"()\-\/]/.test(charAfter);

      if (isBoundaryBefore && isBoundaryAfter) {
        const dedupeKey = `${idx}:${canonical}`;
        if (!seen.has(dedupeKey)) {
          seen.add(dedupeKey);

          // Extract surrounding context (±30 chars)
          const contextStart = Math.max(0, idx - 30);
          const contextEnd = Math.min(transcript.length, idx + variantKey.length + 30);
          const context = transcript.substring(contextStart, contextEnd).trim();

          // Score confidence
          const confidence = scoreConfidence(variantKey, canonical, lowerQuestion);

          // Get the original text as it appeared in the transcript
          const originalText = transcript.substring(idx, idx + variantKey.length);

          candidates.push({
            original: originalText,
            suggested: canonical,
            confidence,
            context: `…${context}…`,
            position: { start: idx, end: idx + variantKey.length }
          });
        }
      }

      searchPos = idx + 1;
    }
  }

  // Sort by position, then by confidence (high first)
  const confidenceOrder = { high: 0, medium: 1, low: 2 };
  candidates.sort((a, b) => {
    if (a.position.start !== b.position.start) return a.position.start - b.position.start;
    return (confidenceOrder[a.confidence] || 2) - (confidenceOrder[b.confidence] || 2);
  });

  return candidates;
}

/**
 * Score how confident we are that a variant should be corrected.
 * Uses edit distance heuristics and question context.
 */
function scoreConfidence(variantKey, canonical, questionContext) {
  const canonicalLower = canonical.toLowerCase();

  // If the question mentions this exact term, higher confidence
  if (questionContext.includes(canonicalLower)) return "high";

  // If the variant is a common abbreviation (all caps, short), medium confidence
  if (variantKey === variantKey.toUpperCase() && variantKey.length <= 5) return "medium";

  // If the variant is very similar to canonical (likely transcription noise), medium
  const editDist = levenshteinDistance(variantKey, canonicalLower);
  if (editDist <= 2) return "medium";

  // Otherwise low — requires human review
  return "low";
}

/**
 * Simple Levenshtein distance implementation.
 */
function levenshteinDistance(a, b) {
  if (a.length === 0) return b.length;
  if (b.length === 0) return a.length;

  const matrix = [];
  for (let i = 0; i <= b.length; i++) matrix[i] = [i];
  for (let j = 0; j <= a.length; j++) matrix[0][j] = j;

  for (let i = 1; i <= b.length; i++) {
    for (let j = 1; j <= a.length; j++) {
      const cost = b[i - 1] === a[j - 1] ? 0 : 1;
      matrix[i][j] = Math.min(
        matrix[i - 1][j] + 1,
        matrix[i][j - 1] + 1,
        matrix[i - 1][j - 1] + cost
      );
    }
  }

  return matrix[b.length][a.length];
}

/**
 * Get the loaded glossary metadata.
 */
function getGlossaryInfo() {
  loadGlossary();
  return {
    loaded: glossaryData !== null && glossaryData.terms.length > 0,
    termCount: glossaryData ? glossaryData.terms.length : 0,
    variantCount: variantMap ? variantMap.size : 0,
    source: GLOSSARY_PATH,
    isTestFixture: GLOSSARY_PATH.includes("test_fixture")
  };
}

/**
 * Find canonical term definition by term or variant name.
 */
function findCanonicalTerm(term) {
  if (!term || typeof term !== "string") return null;
  loadGlossary();
  const lower = term.toLowerCase().trim();
  // Check exact canonical matches
  for (const entry of glossaryData.terms || []) {
    if (entry.canonical.toLowerCase() === lower) {
      return entry;
    }
  }
  // Check variants map
  if (variantMap && variantMap.has(lower)) {
    const { canonical } = variantMap.get(lower);
    return glossaryData.terms.find(t => t.canonical.toLowerCase() === canonical.toLowerCase()) || { canonical };
  }
  return null;
}

module.exports = {
  loadGlossary,
  findCanonicalTerm,
  generateCorrectionCandidates,
  getGlossaryInfo
};

