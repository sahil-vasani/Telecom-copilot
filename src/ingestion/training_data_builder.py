"""
src/ingestion/training_data_builder.py   —   MERGED v3
=======================================================
Merges the original MultiDoc2Dial-grounded pipeline with the improved
telecom-specific BM25 hard-negative mining, sentence-aware chunking,
cross-encoder quality gate, and richer query augmentation.

PRESERVED OUTPUTS (pipeline-critical — do NOT rename):
  data/processed/retriever_train.jsonl      ← merged MD2D + telecom triples
  data/processed/generator_sft_train.jsonl  ← agent-turn SFT pairs
  data/processed/dpo_pairs.jsonl            ← MD2D + SHP-2 preference pairs
  data/processed/test_cases.jsonl           ← MD2D val + handcrafted telecom

ADDED (improvements, optional):
  data/processed/retriever_train_md2d.jsonl     ← MD2D-only triples
  data/processed/retriever_train_telecom.jsonl  ← telecom-only triples
  data/processed/triplets/train_triplets.jsonl  ← BM25-mined train split
  data/processed/triplets/val_triplets.jsonl    ← BM25-mined val split

Run:
    python -m src.ingestion.training_data_builder
    python -m src.ingestion.training_data_builder --use_ce_gate
    python -m src.ingestion.training_data_builder --skip_bm25   (fast mode)
"""

from __future__ import annotations

import json
import random
import argparse
import logging
from pathlib import Path
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional

from datasets import load_from_disk

# ── optional heavy deps (graceful fallback) ───────────────────────────────────
try:
    import nltk
    from nltk.tokenize import sent_tokenize
    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        nltk.download("punkt", quiet=True)
    try:
        nltk.data.find("tokenizers/punkt_tab")
    except LookupError:
        nltk.download("punkt_tab", quiet=True)
    _NLTK_OK = True
except ImportError:
    _NLTK_OK = False

try:
    from rank_bm25 import BM25Okapi
    _BM25_OK = True
except ImportError:
    _BM25_OK = False

random.seed(42)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — INTERNAL DATA STRUCTURES
# (internal only; downstream consumers receive plain dicts)
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class Passage:
    """
    Internal representation used during BM25 hard-negative mining.
    Always converted to plain dict before writing to disk.
    """
    passage_id: str
    text:       str
    domain:     str
    source:     str
    metadata:   dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "passage_id": self.passage_id,
            "section_id": self.metadata.get("section_id", self.passage_id),
            "doc_id":     self.metadata.get("doc_id", "unknown"),
            "text":       self.text,
            "domain":     self.domain,
            "source":     self.source,
            "category":   self.metadata.get("category", self.domain),
            **{k: v for k, v in self.metadata.items()
               if k not in ("section_id", "doc_id", "category")},
        }


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — TELECOM QUERY TEMPLATES  (NEW — query augmentation)
# ══════════════════════════════════════════════════════════════════════════════

TELECOM_QUERY_TEMPLATES: Dict[str, List[str]] = {
    "connectivity": [
        "Why is my {issue} not working on {device}?",
        "How to fix {issue} problem on my phone?",
        "My {issue} keeps dropping, what should I do?",
        "Steps to troubleshoot {issue} issue",
        "{issue} not connecting after SIM change, how to fix?",
        "What causes {issue} to stop working suddenly?",
        "How to improve weak {issue} signal at home?",
    ],
    "apn": [
        "What are the correct APN settings for {carrier}?",
        "How to configure APN on {device} for {carrier} 4G?",
        "APN settings for {carrier} mobile internet",
        "How to set up mobile data APN for {carrier}?",
        "{carrier} internet not working after APN change, fix?",
        "How to fix data not working after entering {carrier} APN?",
        "Correct APN type and proxy for {carrier} network?",
    ],
    "billing": [
        "Why was I charged extra on my {carrier} bill?",
        "How to dispute an incorrect charge on telecom bill?",
        "My {carrier} recharge failed but money was deducted, what to do?",
        "How to get a refund for failed {carrier} recharge?",
        "Why is {carrier} balance not updated after recharge?",
        "How to check bill details and usage on {carrier}?",
        "Unexpected VAS deduction from {carrier} account, how to stop?",
    ],
    "roaming": [
        "How to enable international roaming on {carrier}?",
        "What are {carrier} roaming charges in {country}?",
        "How to activate {carrier} international roaming pack?",
        "My {carrier} SIM shows no service abroad, what to do?",
        "How to use {carrier} SIM in {country} without extra charges?",
        "Best {carrier} international plan for {country} travel?",
        "How to avoid roaming bill shock with {carrier}?",
    ],
    "sim": [
        "How to port my mobile number to {carrier}?",
        "How to activate new {carrier} SIM card?",
        "How to upgrade {carrier} SIM from 3G to 4G?",
        "Documents required for {carrier} SIM verification?",
        "How many days does {carrier} number porting take?",
        "My {carrier} SIM is not working after insertion, how to fix?",
        "How to get a duplicate {carrier} SIM if my SIM is lost?",
    ],
    "ivr_complaint": [
        "How to raise a complaint with {carrier} customer care?",
        "What is {carrier} toll-free customer care number?",
        "How to escalate unresolved complaint to {carrier}?",
        "How many days for {carrier} to resolve a complaint?",
        "How to file a complaint against {carrier} with TRAI?",
        "What is the grievance redressal process for {carrier}?",
        "How to stop unwanted promotional calls from {carrier}?",
    ],
    # Fallback for MD2D domains (government / procedures / benefits)
    "procedures": [
        "How do I complete {issue} procedure?",
        "What documents are needed for {issue}?",
        "Steps to apply for {issue}",
        "What is the process to {issue}?",
    ],
    "benefits": [
        "Am I eligible for {issue} benefits?",
        "How to claim {issue}?",
        "What are the requirements for {issue}?",
    ],
}

_CARRIERS  = ["Jio", "Airtel", "Vi", "BSNL", "MTNL"]
_DEVICES   = ["Android", "iPhone", "Samsung", "OnePlus", "Xiaomi"]
_COUNTRIES = ["USA", "UK", "UAE", "Singapore", "Australia"]
_ISSUES    = ["5G", "4G LTE", "mobile data", "WiFi calling", "VoLTE",
              "internet", "network signal", "mobile hotspot"]


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — PASSAGE QUALITY HELPERS  (NEW)
# ══════════════════════════════════════════════════════════════════════════════

_TELECOM_KW = {
    "sim", "5g", "4g", "lte", "volte", "apn", "network", "signal", "roaming",
    "recharge", "plan", "prepaid", "postpaid", "data", "calling", "sms",
    "carrier", "operator", "jio", "airtel", "bsnl", "vi", "vodafone",
    "billing", "balance", "complaint", "porting", "activation", "coverage",
    "internet", "hotspot", "tethering", "bandwidth", "latency", "imei",
    "esim", "kyc", "aadhaar", "trai", "mnp", "fup", "dnd", "vas", "ivr",
}


def is_quality_passage(text: str, min_words: int = 20, max_words: int = 350) -> bool:
    wc = len(text.split())
    return min_words <= wc <= max_words


def telecom_relevance_score(text: str) -> float:
    words = set(text.lower().split())
    return min(len(words & _TELECOM_KW) / 4.0, 1.0)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — SENTENCE-AWARE CHUNKING  (NEW)
# ══════════════════════════════════════════════════════════════════════════════

def sentence_aware_chunk(
    text: str,
    max_tokens: int = 128,
    overlap_sentences: int = 1,
    min_tokens: int = 25,
) -> List[str]:
    """
    Split text at sentence boundaries with configurable overlap.
    Falls back to splitting on '. ' when NLTK is unavailable.
    Token count approximated as word_count × 1.3.
    """
    if _NLTK_OK:
        sentences = sent_tokenize(text)
    else:
        sentences = [s.strip() for s in text.split(". ") if s.strip()]

    chunks: List[str] = []
    current_sents: List[str] = []
    current_len = 0

    for sent in sentences:
        sent_len = int(len(sent.split()) * 1.3)
        if current_len + sent_len > max_tokens and current_sents:
            chunk_text = " ".join(current_sents).strip()
            if int(len(chunk_text.split()) * 1.3) >= min_tokens:
                chunks.append(chunk_text)
            current_sents = current_sents[-overlap_sentences:] if overlap_sentences else []
            current_len = sum(int(len(s.split()) * 1.3) for s in current_sents)
        current_sents.append(sent)
        current_len += sent_len

    if current_sents:
        chunk_text = " ".join(current_sents).strip()
        if int(len(chunk_text.split()) * 1.3) >= min_tokens:
            chunks.append(chunk_text)

    return chunks or [text.strip()]


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — SYNTHETIC QUERY GENERATION  (NEW)
# ══════════════════════════════════════════════════════════════════════════════

def generate_queries_for_passage(passage: Passage, n: int = 3) -> List[str]:
    """
    Generates n synthetic queries for a passage via three strategies:
      A) Domain template + random slot fill
      B) First sentence → how-to question
      C) Action keyword extraction
    """
    queries: List[str] = []
    domain = passage.domain if passage.domain in TELECOM_QUERY_TEMPLATES else "connectivity"
    templates = TELECOM_QUERY_TEMPLATES[domain]

    # A) Template
    for tmpl in random.sample(templates, min(2, len(templates))):
        q = tmpl.format(
            issue=random.choice(_ISSUES),
            carrier=random.choice(_CARRIERS),
            device=random.choice(_DEVICES),
            country=random.choice(_COUNTRIES),
        )
        queries.append(q)

    # B) First sentence
    if _NLTK_OK:
        try:
            sents = sent_tokenize(passage.text)
            if sents and len(sents[0].split()) > 6:
                first = sents[0].strip()
                q = first if first.endswith("?") else f"How to handle: {first[:90]}?"
                queries.append(q)
        except Exception:
            pass
    else:
        first = passage.text[:120].strip()
        if len(first.split()) > 6:
            queries.append(f"How to handle: {first[:90]}?")

    # C) Action keywords
    text_lower = passage.text.lower()
    for kw in ["to activate", "to fix", "to configure", "to resolve",
                "to enable", "to port", "to upgrade", "to block"]:
        idx = text_lower.find(kw)
        if idx != -1:
            snippet = passage.text[idx: idx + 65].strip()
            queries.append(f"How {snippet}?")
            break

    # Deduplicate
    seen: set = set()
    unique: List[str] = []
    for q in queries:
        q = q.strip()
        if q and q not in seen and len(q.split()) >= 4:
            seen.add(q)
            unique.append(q)
    return unique[:n]


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — BM25 HARD-NEGATIVE MINER  (NEW)
# ══════════════════════════════════════════════════════════════════════════════

class HardNegativeMiner:
    """
    Builds a BM25Okapi index over a corpus of Passage objects.
    For each (query, positive) pair, returns lexically-similar passages
    that are NOT the positive — these are hard negatives that force the
    retriever to learn fine-grained semantic distinctions.

    Falls back to random sampling when rank_bm25 is not installed.
    """

    def __init__(self, passages: List[Passage]):
        self.passages = passages
        if not _BM25_OK:
            log.warning("rank_bm25 not installed. Falling back to random negatives. "
                        "pip install rank_bm25")
            self._bm25 = None
        else:
            tokenized = [p.text.lower().split() for p in passages]
            log.info(f"  Building BM25 index over {len(passages):,} passages …")
            self._bm25 = BM25Okapi(tokenized)
            log.info("  BM25 index ready.")

    def get_hard_negatives(
        self,
        query:       str,
        positive_id: str,
        n:           int = 2,
        top_k:       int = 25,
    ) -> List[Passage]:
        if self._bm25 is None:
            # Fallback: random passages that are not the positive
            pool = [p for p in self.passages if p.passage_id != positive_id]
            return random.sample(pool, min(n, len(pool)))

        import numpy as np
        scores = self._bm25.get_scores(query.lower().split())
        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        hard_negs: List[Passage] = []
        for idx in ranked[: top_k + 5]:
            p = self.passages[idx]
            if p.passage_id == positive_id:
                continue
            if scores[idx] > 0.0:
                hard_negs.append(p)
            if len(hard_negs) >= n:
                break
        return hard_negs


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — CROSS-ENCODER QUALITY GATE  (NEW — optional)
# ══════════════════════════════════════════════════════════════════════════════

class CrossEncoderGate:
    """
    Optional quality filter: keeps only triplets where
        CE(q, positive) − CE(q, negative) ≥ margin.
    Requires sentence-transformers.  Safe to skip (--use_ce_gate omitted).
    """

    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        device:     str = "cpu",
        batch_size: int = 16,
    ):
        from sentence_transformers import CrossEncoder
        log.info(f"  Loading CrossEncoder: {model_name} on {device}")
        self.model      = CrossEncoder(model_name, device=device, max_length=256)
        self.batch_size = batch_size

    def _score_pairs(self, pairs: List[Tuple[str, str]]) -> List[float]:
        import numpy as np
        all_scores: List[float] = []
        for i in range(0, len(pairs), self.batch_size):
            batch = pairs[i: i + self.batch_size]
            batch_scores = self.model.predict(batch)
            # predict can return ndarray or list
            if hasattr(batch_scores, "tolist"):
                batch_scores = batch_scores.tolist()
            all_scores.extend(batch_scores)
        return all_scores

    def filter_triplets(
        self,
        triplets: List[Dict],
        margin:   float = 1.0,
    ) -> List[Dict]:
        if not triplets:
            return []
        log.info(f"  CE gate: scoring {len(triplets):,} triplets …")
        pos_scores = self._score_pairs(
            [(t["query"], t["positive_text"]) for t in triplets]
        )
        neg_scores = self._score_pairs(
            [(t["query"], t.get("hard_negative_text", "")) for t in triplets]
        )
        kept = [
            {**t, "ce_score_pos": round(float(ps), 4),
                  "ce_score_neg": round(float(ns), 4)}
            for t, ps, ns in zip(triplets, pos_scores, neg_scores)
            if ps - ns >= margin
        ]
        log.info(f"  CE gate passed: {len(kept):,}/{len(triplets):,} "
                 f"(margin={margin})")
        return kept


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 8 — DEDUPLICATION  (NEW)
# ══════════════════════════════════════════════════════════════════════════════

def deduplicate_triples(triples: List[Dict]) -> List[Dict]:
    """Remove exact (query[:60], positive_id, first-hard-neg) duplicates."""
    seen: set = set()
    unique: List[Dict] = []
    for t in triples:
        first_neg = t.get("hard_negatives", [""])[0] if t.get("hard_negatives") else ""
        key = (t.get("query", "")[:60], t.get("positive_id", ""), first_neg)
        if key not in seen:
            seen.add(key)
            unique.append(t)
    removed = len(triples) - len(unique)
    if removed:
        log.info(f"  Deduplication removed {removed:,} duplicates.")
    return unique


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 9 — RESOURCE LOADER  (PRESERVED from old)
# ══════════════════════════════════════════════════════════════════════════════

def load_resources(
    dial_path:     str = "data/raw/multidoc2dial/dialogues",
    span_idx_path: str = "data/processed/span_index.json",
) -> Tuple:
    print("  Loading dialogues …")
    dial_ds = load_from_disk(dial_path)
    print("  Loading span index …")
    with open(span_idx_path) as f:
        span_index = json.load(f)
    return dial_ds, span_index


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 10 — A. MD2D RETRIEVER TRIPLES  (PRESERVED + BM25 upgrade)
# ══════════════════════════════════════════════════════════════════════════════

def build_retriever_triples(
    dial_ds,
    span_index:  Dict,
    split:       str = "train",
    output_path: str = "data/processed/retriever_train_md2d.jsonl",
    max_samples: int = 10000,
    use_bm25:    bool = True,
) -> List[Dict]:
    """
    For each USER turn in MD2D that has grounding references, extracts:
        (user_query, positive_section_id, hard_negative_section_ids)

    IMPROVEMENT: when use_bm25=True, hard negatives are mined with BM25
    (lexically confusable spans) rather than random same-doc spans.
    Falls back to same-doc random negatives when BM25 is unavailable or
    use_bm25=False.

    Output schema (preserved for train_retriever.py):
    {
        "query":          str,
        "positive_id":    str,   # section_id   ← required by train_retriever
        "positive_text":  str,
        "hard_negatives": [str], # list of section_ids
        "doc_id":         str,
        "domain":         str,
        "source":         "multidoc2dial",
    }
    """
    print(f"\n  Building MD2D retriever triples from '{split}' split …")

    # Group all spans by doc_id for fallback same-doc negatives
    doc_to_spans: Dict[str, List[str]] = defaultdict(list)
    for sec_id, passage in span_index.items():
        doc_to_spans[passage["doc_id"]].append(sec_id)

    # ── Optional: build Passage objects for BM25 ──────────────────
    bm25_miner: Optional[HardNegativeMiner] = None
    if use_bm25 and _BM25_OK:
        bm25_passages = [
            Passage(
                passage_id=sec_id,
                text=p["text"],
                domain=p.get("domain", "unknown"),
                source="multidoc2dial",
                metadata={"section_id": sec_id, "doc_id": p["doc_id"]},
            )
            for sec_id, p in span_index.items()
            if p.get("text")
        ]
        bm25_miner = HardNegativeMiner(bm25_passages)

    dataset = dial_ds[split]
    triples: List[Dict] = []

    for dialogue in dataset:
        turns = dialogue.get("turns", [])
        for sample in turns:
            role = sample.get("role", sample.get("speaker", ""))
            if role != "user":
                continue
            refs = sample.get("references", [])
            if not refs:
                continue
            query = sample["utterance"].strip()
            if len(query) < 10:
                continue

            for ref in refs:
                if ref.get("label") not in ("solution", "precondition"):
                    continue

                doc_id  = ref["doc_id"]
                span_id = ref["id_sp"]
                sec_id  = f"{doc_id}__sp{span_id}"

                if sec_id not in span_index:
                    continue

                positive_passage = span_index[sec_id]

                # ── Hard negative selection ──────────────────────
                if bm25_miner is not None:
                    bm25_negs = bm25_miner.get_hard_negatives(
                        query, sec_id, n=3
                    )
                    hard_neg_ids = [p.passage_id for p in bm25_negs]
                else:
                    # Fallback: random same-doc spans
                    same_doc = [s for s in doc_to_spans[doc_id] if s != sec_id]
                    hard_neg_ids = random.sample(same_doc, min(3, len(same_doc)))

                triples.append({
                    "query":          query,
                    "positive_id":    sec_id,
                    "positive_text":  positive_passage["text"],
                    "hard_negatives": hard_neg_ids,
                    "doc_id":         doc_id,
                    "domain":         positive_passage.get("domain", "unknown"),
                    "source":         "multidoc2dial",
                })

                if len(triples) >= max_samples:
                    break
            if len(triples) >= max_samples:
                break
        if len(triples) >= max_samples:
            break

    triples = deduplicate_triples(triples)
    random.shuffle(triples)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        for t in triples:
            f.write(json.dumps(t) + "\n")
    print(f"  Saved {len(triples):,} MD2D retriever triples → {output_path}")
    return triples


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 11 — B. TELECOM RETRIEVER TRIPLES  (MERGED — BM25 + query augment)
# ══════════════════════════════════════════════════════════════════════════════

def _load_telecom_passages_as_objects(
    telecom_path: str,
) -> List[Passage]:
    """
    Loads telecom passages from JSONL and wraps them in Passage objects,
    guaranteeing all required fields exist (no KeyError downstream).
    """
    passages: List[Passage] = []
    path = Path(telecom_path)
    if not path.exists():
        log.warning(f"  Telecom KB not found: {telecom_path}")
        return passages

    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError:
                continue

            text = raw.get("text", "").strip()
            if not is_quality_passage(text):
                continue

            # --- Guarantee all ID fields exist ---
            passage_id = raw.get(
                "passage_id",
                raw.get("section_id", f"telecom_p{i}")
            )
            section_id = raw.get("section_id", passage_id)
            doc_id     = raw.get("doc_id", "telecom_generated")
            category   = raw.get("category", raw.get("domain", "telecom"))
            domain     = raw.get("domain", "telecom")
            source     = raw.get("source", "telecom_kb")

            passages.append(Passage(
                passage_id=passage_id,
                text=text,
                domain=domain,
                source=source,
                metadata={
                    "section_id": section_id,
                    "doc_id":     doc_id,
                    "category":   category,
                    "heading":    raw.get("heading", ""),
                    "title":      raw.get("title", category),
                },
            ))

    log.info(f"  Loaded {len(passages):,} telecom passages from {telecom_path}")
    return passages


def build_telecom_retriever_triples(
    telecom_path: str = "data/raw/telecom_kb/passages.jsonl",
    output_path:  str = "data/processed/retriever_train_telecom.jsonl",
    use_bm25:     bool = True,
    n_queries:    int = 3,
    n_hard:       int = 2,
    n_easy:       int = 1,
    max_triplets: int = 20000,
) -> List[Dict]:
    """
    Builds telecom retriever triples using:
      - BM25 hard negatives (lexically confusable passages)
      - Cross-domain easy negatives
      - Augmented queries from TELECOM_QUERY_TEMPLATES

    IMPROVEMENT over old version:
      Old: category-based negative (1 random neg per passage).
      New: BM25 hard negatives + cross-domain easy negatives
           + multiple augmented queries per passage.

    Output schema is identical to MD2D triples for compatibility:
    {
        "query":          str,
        "positive_id":    str,
        "positive_text":  str,
        "hard_negatives": [str],
        "doc_id":         str,
        "domain":         str,
        "source":         "telecom_kb",
        "negative_types": List[str],
    }
    """
    print("\n  Building telecom retriever triples …")

    passages = _load_telecom_passages_as_objects(telecom_path)
    if not passages:
        log.warning("  No telecom passages found. Returning empty list.")
        return []

    # ── BM25 miner ────────────────────────────────────────────────
    miner: Optional[HardNegativeMiner] = None
    if use_bm25 and _BM25_OK:
        miner = HardNegativeMiner(passages)

    # ── Domain index for cross-domain easy negatives ──────────────
    domain_index: Dict[str, List[Passage]] = defaultdict(list)
    for p in passages:
        domain_index[p.domain].append(p)
    all_domains = list(domain_index.keys())

    triples: List[Dict] = []

    for pos in passages:
        if len(triples) >= max_triplets:
            break

        queries = generate_queries_for_passage(pos, n=n_queries)

        for query in queries:
            if len(triples) >= max_triplets:
                break

            neg_ids:   List[str] = []
            neg_types: List[str] = []

            # Hard negatives (BM25)
            if miner is not None:
                bm25_negs = miner.get_hard_negatives(
                    query, pos.passage_id, n=n_hard
                )
            else:
                # Fallback: random pool excluding positive
                pool = [p for p in passages if p.passage_id != pos.passage_id]
                bm25_negs = random.sample(pool, min(n_hard, len(pool)))

            for neg in bm25_negs:
                neg_ids.append(neg.passage_id)
                neg_types.append("bm25_hard")

            # Easy cross-domain negatives
            other_domains = [d for d in all_domains if d != pos.domain]
            if other_domains:
                for _ in range(n_easy):
                    easy_neg = random.choice(
                        domain_index[random.choice(other_domains)]
                    )
                    neg_ids.append(easy_neg.passage_id)
                    neg_types.append("cross_domain_easy")

            if not neg_ids:
                continue

            triples.append({
                "query":          query,
                "positive_id":    pos.passage_id,
                "positive_text":  pos.text,
                "hard_negatives": neg_ids,
                "doc_id":         pos.metadata.get("doc_id", "telecom_generated"),
                "domain":         pos.domain,
                "source":         "telecom_kb",
                "negative_types": neg_types,
                # Flat first hard-negative text for cross-encoder gate
                "hard_negative_text": passages[
                    next((i for i, p in enumerate(passages)
                          if p.passage_id == neg_ids[0]), 0)
                ].text if neg_ids else "",
            })

    triples = deduplicate_triples(triples)
    random.shuffle(triples)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        for t in triples:
            f.write(json.dumps(t) + "\n")
    print(f"  Saved {len(triples):,} telecom retriever triples → {output_path}")
    return triples


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 12 — C. GENERATOR SFT PAIRS  (PRESERVED from old — unchanged)
# ══════════════════════════════════════════════════════════════════════════════

def build_generator_sft_pairs(
    dial_ds,
    span_index:  Dict,
    split:       str = "train",
    output_path: str = "data/processed/generator_sft_train.jsonl",
    max_samples: int = 8000,
) -> List[Dict]:
    """
    For each AGENT turn with grounding references, extracts:
        (query=previous user turn, context=grounding spans, gold_answer=agent utterance)

    This is the exact setup for supervised fine-tuning the generator:
    given a user question + retrieved context → produce a grounded cited answer.

    Output schema (required by src/generation/train_generator.py):
    {
        "query":          str,
        "context":        [{"section_id", "doc_id", "heading", "text"}],
        "gold_answer":    str,
        "gold_citations": [{"doc_id", "section_id", "span_id"}],
        "domain":         str,
        "dialogue_id":    str,
        "turn_id":        int,
        "source":         "multidoc2dial",
    }
    """
    print(f"\n  Building generator SFT pairs from '{split}' split …")

    dataset = dial_ds[split]
    dialogues: Dict[str, List] = {}
    for dialogue in dataset:
        dia_id = dialogue.get("dial_id", "unknown")
        dialogues[dia_id] = dialogue.get("turns", [])

    pairs: List[Dict] = []

    for dial_id, turns in dialogues.items():
        turns_sorted = sorted(turns, key=lambda t: t.get("turn_id", 0))

        for i, turn in enumerate(turns_sorted):
            role = turn.get("role", turn.get("speaker", ""))
            if role != "agent":
                continue
            refs = turn.get("references", [])
            if not refs:
                continue
            agent_answer = turn["utterance"].strip()
            if len(agent_answer) < 20:
                continue

            prev_user_turns = [
                t for t in turns_sorted[:i]
                if t.get("role", t.get("speaker", "")) == "user"
            ]
            if not prev_user_turns:
                continue
            query = prev_user_turns[-1]["utterance"].strip()

            context_passages: List[Dict] = []
            citations:        List[Dict] = []

            for ref in refs:
                if ref.get("label") not in ("solution", "precondition"):
                    continue
                doc_id  = ref["doc_id"]
                span_id = ref["id_sp"]
                sec_id  = f"{doc_id}__sp{span_id}"
                if sec_id not in span_index:
                    continue
                passage = span_index[sec_id]
                context_passages.append({
                    "section_id": sec_id,
                    "doc_id":     doc_id,
                    "heading":    passage.get("heading", ""),
                    "text":       passage["text"],
                })
                citations.append({
                    "doc_id":     doc_id,
                    "section_id": sec_id,
                    "span_id":    span_id,
                })

            if not context_passages:
                continue

            # Resolve domain safely
            domain = (
                context_passages[0].get("domain")
                or span_index.get(citations[0]["section_id"], {}).get("domain", "unknown")
            )

            pairs.append({
                "query":          query,
                "context":        context_passages,
                "gold_answer":    agent_answer,
                "gold_citations": citations,
                "domain":         domain,
                "dialogue_id":    dial_id,
                "turn_id":        turn.get("turn_id", i),
                "source":         "multidoc2dial",
            })

            if len(pairs) >= max_samples:
                break
        if len(pairs) >= max_samples:
            break

    random.shuffle(pairs)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        for p in pairs:
            f.write(json.dumps(p) + "\n")
    print(f"  Saved {len(pairs):,} generator SFT pairs → {output_path}")
    return pairs


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 13 — D. DPO PREFERENCE PAIRS  (PRESERVED from old — unchanged)
# ══════════════════════════════════════════════════════════════════════════════

def build_dpo_pairs(
    sft_pairs:     List[Dict],
    shp2_path:     str = "data/raw/shp2",
    output_path:   str = "data/processed/dpo_pairs.jsonl",
    max_from_md2d: int = 1000,
    max_from_shp2: int = 1000,
) -> List[Dict]:
    """
    Builds DPO preference pairs from two sources:
      Source 1 — MD2D-derived: chosen=gold agent answer (grounded, concise),
                                rejected=bloated hedged version
      Source 2 — SHP-2 filtered: chosen=higher-upvoted, rejected=lower-upvoted

    Output schema (required by DPO trainer):
    {
        "prompt":   str,
        "chosen":   str,
        "rejected": str,
        "source":   "md2d" | "shp2",
        "domain":   str,
    }
    """
    print(f"\n  Building DPO pairs …")
    dpo_pairs: List[Dict] = []

    # ── Source 1: MD2D-derived ────────────────────────────────────
    print(f"  Building {max_from_md2d} MD2D-derived DPO pairs …")

    def make_rejected_response(chosen: str, _citations: List[Dict]) -> str:
        return (
            "That's a great question. There are many factors to consider here. "
            "Generally speaking, it depends on various circumstances. "
            + chosen
            + " However, please note that policies may vary and you should always "
            "check the official website for the most up-to-date information. "
            "Is there anything else I can help you with today?"
        )

    sample_sft = random.sample(sft_pairs, min(max_from_md2d, len(sft_pairs)))
    for pair in sample_sft:
        chosen    = pair["gold_answer"]
        citations = pair["gold_citations"]
        doc_id    = citations[0]["doc_id"] if citations else "unknown"
        span_id   = citations[0]["span_id"] if citations else "?"
        chosen_with_citation = f"{chosen} [SOURCE: {doc_id}, span {span_id}]"
        rejected  = make_rejected_response(chosen, citations)
        prompt    = (
            f"Customer asked: {pair['query']}\n"
            f"Context: {pair['context'][0]['text'][:300] if pair['context'] else ''}"
        )
        dpo_pairs.append({
            "prompt":   prompt,
            "chosen":   chosen_with_citation,
            "rejected": rejected,
            "source":   "md2d",
            "domain":   pair.get("domain", "unknown"),
        })

    # ── Source 2: SHP-2 ──────────────────────────────────────────
    print(f"  Loading SHP-2 pairs …")
    try:
        shp2_ds   = load_from_disk(shp2_path)
        shp2_list = list(shp2_ds)
        random.shuffle(shp2_list)
        added = 0
        for sample in shp2_list:
            if added >= max_from_shp2:
                break
            if sample["labels"] == 1:
                chosen, rejected = sample["human_ref_A"], sample["human_ref_B"]
            else:
                chosen, rejected = sample["human_ref_B"], sample["human_ref_A"]
            if len(chosen) < 50 or len(rejected) < 50:
                continue
            if abs(len(chosen) - len(rejected)) < 20:
                continue
            dpo_pairs.append({
                "prompt":      sample["history"][:400],
                "chosen":      chosen[:600],
                "rejected":    rejected[:600],
                "source":      "shp2",
                "domain":      sample.get("domain", "unknown"),
                "score_ratio": sample.get("score_ratio", 1.0),
            })
            added += 1
        print(f"  Added {added} SHP-2 pairs.")
    except Exception as e:
        print(f"  Warning: Could not load SHP-2 ({e}). Continuing with MD2D pairs only.")

    random.shuffle(dpo_pairs)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        for p in dpo_pairs:
            f.write(json.dumps(p) + "\n")

    src_counts = Counter(p["source"] for p in dpo_pairs)
    print(f"  Saved {len(dpo_pairs):,} DPO pairs → {output_path}")
    print(f"    md2d: {src_counts['md2d']:,}  |  shp2: {src_counts['shp2']:,}")
    return dpo_pairs


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 14 — E. EVALUATION TEST SET  (PRESERVED from old — unchanged)
# ══════════════════════════════════════════════════════════════════════════════

def build_eval_test_set(
    dial_ds,
    span_index:  Dict,
    output_path: str = "data/processed/test_cases.jsonl",
    n_cases:     int = 200,
) -> List[Dict]:
    """
    Builds the evaluation test set from the VALIDATION split of MultiDoc2Dial.
    Using the validation split ensures no data leakage.

    Output schema (required by evaluation pipeline):
    {
        "test_id":               str,
        "source":                str,
        "query":                 str,
        "history":               List[Dict],
        "gold_doc_id":           str,
        "gold_section_id":       str,
        "gold_answer":           str,
        "gold_tool":             str,
        "should_escalate":       bool,
        "requires_outage_check": bool,
        "category":              str,
        "domain":                str,
    }
    """
    print(f"\n  Building eval test set from validation split …")
    val_ds  = dial_ds["validation"]
    cases:  List[Dict] = []
    seen:   set = set()

    dialogues: Dict[str, List] = {}
    for dialogue in val_ds:
        dia_id = dialogue.get("dial_id", "unknown")
        dialogues[dia_id] = dialogue.get("turns", [])

    for dial_id, turns in dialogues.items():
        if len(cases) >= n_cases:
            break
        turns_sorted = sorted(turns, key=lambda t: t.get("turn_id", 0))

        for i, turn in enumerate(turns_sorted):
            role = turn.get("role", turn.get("speaker", ""))
            if role != "agent":
                continue
            refs = turn.get("references", [])
            if not refs:
                continue
            agent_answer = turn["utterance"].strip()
            if len(agent_answer) < 20:
                continue
            prev_user = [
                t for t in turns_sorted[:i]
                if t.get("role", t.get("speaker", "")) == "user"
            ]
            if not prev_user:
                continue
            query = prev_user[-1]["utterance"].strip()
            if query in seen:
                continue
            seen.add(query)

            ref    = refs[0]
            doc_id = ref["doc_id"]
            span_id = ref["id_sp"]
            sec_id  = f"{doc_id}__sp{span_id}"
            if sec_id not in span_index:
                continue

            history = [
                {"role": prev["role"], "utterance": prev["utterance"]}
                for prev in turns_sorted[max(0, i - 4):i]
            ]
            cases.append({
                "test_id":               f"MD2D_VAL_{len(cases)+1:04d}",
                "source":                "multidoc2dial_validation",
                "query":                 query,
                "history":               history,
                "gold_doc_id":           doc_id,
                "gold_section_id":       sec_id,
                "gold_answer":           agent_answer,
                "gold_tool":             "SearchKB",
                "should_escalate":       False,
                "requires_outage_check": False,
                "category":              span_index[sec_id].get("domain", "unknown"),
                "domain":                span_index[sec_id].get("domain", "unknown"),
            })
            if len(cases) >= n_cases:
                break

    # ── Handcrafted telecom test cases (preserved verbatim) ────────
    telecom_cases = [
        {
            "test_id": "TELECOM_001",
            "source": "telecom_handcrafted",
            "query": "I was charged roaming fees but I never left India.",
            "history": [],
            "gold_doc_id": "telecom_roaming_001",
            "gold_section_id": "telecom_roaming_001_s3",
            "gold_answer": (
                "Being charged roaming rates while in India is a valid dispute reason. "
                "Submit a dispute within 60 days of the bill date via the portal or by "
                "calling 198. Disputed amounts are held and not collected until resolution."
            ),
            "gold_tool": "GetPolicy",
            "should_escalate": False,
            "requires_outage_check": False,
            "category": "roaming",
            "domain": "telecom",
        },
        {
            "test_id": "TELECOM_002",
            "source": "telecom_handcrafted",
            "query": "My 4G is completely down in Ahmedabad since this morning.",
            "history": [],
            "gold_doc_id": "telecom_network_001",
            "gold_section_id": "telecom_network_001_s3",
            "gold_answer": (
                "I'll check the current network status for Ahmedabad. If there is an active "
                "outage, our target restoration time is 4 hours for urban areas with updates "
                "every 2 hours on our app."
            ),
            "gold_tool": "CheckNetworkStatus",
            "should_escalate": False,
            "requires_outage_check": True,
            "category": "network",
            "domain": "telecom",
            "region": "Ahmedabad",
            "service_type": "4G",
        },
        {
            "test_id": "TELECOM_003",
            "source": "telecom_handcrafted",
            "query": "This billing issue has been going on for 10 days and nobody has resolved it.",
            "history": [
                {"role": "user", "utterance": "There is a wrong charge of Rs. 3000 on my bill."},
                {"role": "agent", "utterance": "A dispute ticket has been raised for you."},
            ],
            "gold_doc_id": "telecom_escalation_001",
            "gold_section_id": "telecom_escalation_001_s2",
            "gold_answer": (
                "Since the issue has been unresolved for more than 7 working days, this "
                "qualifies for escalation to our Nodal Officer. Please email "
                "nodal@telecom.com with your original ticket ID. "
                "Target resolution is 3 working days."
            ),
            "gold_tool": "CreateTicket",
            "should_escalate": True,
            "requires_outage_check": False,
            "category": "escalation",
            "domain": "telecom",
        },
        {
            "test_id": "TELECOM_004",
            "source": "telecom_handcrafted",
            "query": "I got a bill for Rs. 15,000 in roaming charges for a 3-day trip.",
            "history": [],
            "gold_doc_id": "telecom_roaming_001",
            "gold_section_id": "telecom_roaming_001_s3",
            "gold_answer": (
                "A charge of Rs. 15,000 for 3 days of roaming is likely incorrect. "
                "This is a high-value dispute. I am escalating this to our senior billing "
                "team and creating a ticket. Disputed amounts are held and not collected "
                "until resolved."
            ),
            "gold_tool": "CreateTicket",
            "should_escalate": True,
            "requires_outage_check": False,
            "category": "roaming",
            "domain": "telecom",
        },
        {
            "test_id": "TELECOM_005",
            "source": "telecom_handcrafted",
            "query": "How do I switch to eSIM?",
            "history": [],
            "gold_doc_id": "telecom_device_001",
            "gold_section_id": "telecom_device_001_s2",
            "gold_answer": (
                "Go to My Account > SIM Management > Switch to eSIM. A QR code is sent "
                "to your registered email. Scan it in your device settings to activate. "
                "eSIM is supported on iPhone XS and later, Samsung Galaxy S20 and later."
            ),
            "gold_tool": "SearchKB",
            "should_escalate": False,
            "requires_outage_check": False,
            "category": "device",
            "domain": "telecom",
        },
    ]
    cases.extend(telecom_cases)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        for c in cases:
            f.write(json.dumps(c) + "\n")

    src_counts = Counter(c["source"] for c in cases)
    print(f"  Saved {len(cases):,} test cases → {output_path}")
    print(f"    multidoc2dial_validation: {src_counts['multidoc2dial_validation']:,}")
    print(f"    telecom_handcrafted:      {src_counts['telecom_handcrafted']:,}")
    return cases


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 15 — OPTIONAL: BM25-MINED SPLIT FILES  (NEW)
# Writes train_triplets.jsonl / val_triplets.jsonl for advanced training runs.
# Does NOT replace the pipeline-critical retriever_train.jsonl.
# ══════════════════════════════════════════════════════════════════════════════

def save_triplet_splits(
    triples:   List[Dict],
    out_dir:   str = "data/processed/triplets",
    val_ratio: float = 0.1,
) -> None:
    """
    Saves BM25-mined triples in a separate directory as train/val splits.
    Optionally also exports HuggingFace Dataset format.
    These files are consumed by advanced retriever training runs that
    want separate val monitoring — they do NOT replace retriever_train.jsonl.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    random.shuffle(triples)
    split_idx = int(len(triples) * (1 - val_ratio))
    splits = {
        "train": triples[:split_idx],
        "val":   triples[split_idx:],
    }
    for name, data in splits.items():
        path = out / f"{name}_triplets.jsonl"
        with open(path, "w") as f:
            for t in data:
                f.write(json.dumps(t) + "\n")
        log.info(f"  Saved {len(data):,} {name} triplets → {path}")

    # Optional HuggingFace Dataset output
    try:
        from datasets import Dataset
        for name, data in splits.items():
            Dataset.from_list(data).save_to_disk(str(out / f"hf_{name}"))
            log.info(f"  HF dataset → {out}/hf_{name}")
    except Exception as e:
        log.warning(f"  HF dataset save skipped: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 16 — MAIN ORCHESTRATOR  (PRESERVED + extended)
# ══════════════════════════════════════════════════════════════════════════════

def build_all_training_data(
    use_bm25:    bool = True,
    use_ce_gate: bool = False,
    ce_margin:   float = 1.0,
    save_splits: bool = False,
) -> None:
    """
    Full pipeline orchestrator.
    Called by:  python -m src.ingestion.training_data_builder

    Steps:
      A. MD2D Retriever Triples  (BM25 hard negatives when available)
      B. Telecom Synthetic Triples  (BM25 + query augmentation)
      C. Merge → retriever_train.jsonl  (pipeline-critical path)
      D. Optional: CE quality gate + split files
      E. Generator SFT Pairs
      F. DPO Preference Pairs
      G. Evaluation Test Set
    """
    import sys
    sys.path.insert(0, ".")

    dial_ds, span_index = load_resources()

    # ── A: MD2D Retriever Triples ──────────────────────────────────
    md2d_triples = build_retriever_triples(
        dial_ds,
        span_index,
        output_path="data/processed/retriever_train_md2d.jsonl",
        max_samples=30000,
        use_bm25=use_bm25,
    )

    # ── B: Telecom Synthetic Triples ───────────────────────────────
    telecom_triples = build_telecom_retriever_triples(
        telecom_path="data/raw/telecom_kb/passages.jsonl",
        output_path="data/processed/retriever_train_telecom.jsonl",
        use_bm25=use_bm25,
    )

    # ── C: Merge → pipeline-critical retriever_train.jsonl ─────────
    all_triples = md2d_triples + telecom_triples
    random.shuffle(all_triples)

    # ── D: Optional CE quality gate ────────────────────────────────
    if use_ce_gate and all_triples:
        # Filter only triples that have a hard_negative_text field
        gateable = [t for t in all_triples if t.get("hard_negative_text")]
        rest     = [t for t in all_triples if not t.get("hard_negative_text")]
        try:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
            gate   = CrossEncoderGate(device=device, batch_size=16)
            gateable = gate.filter_triplets(gateable, margin=ce_margin)
        except Exception as e:
            log.warning(f"  CE gate skipped: {e}")
        all_triples = gateable + rest
        random.shuffle(all_triples)

    final_retriever_path = "data/processed/retriever_train.jsonl"
    Path(final_retriever_path).parent.mkdir(parents=True, exist_ok=True)
    with open(final_retriever_path, "w", encoding="utf-8") as f:
        for t in all_triples:
            f.write(json.dumps(t) + "\n")

    print(f"\n  Final merged retriever triples: {len(all_triples):,}")
    print(f"  Saved merged triples → {final_retriever_path}")

    # Optional: save separate train/val splits
    if save_splits:
        save_triplet_splits(all_triples)

    # ── E: Generator SFT Pairs ─────────────────────────────────────
    sft_pairs = build_generator_sft_pairs(
        dial_ds,
        span_index,
        output_path="data/processed/generator_sft_train.jsonl",
        max_samples=20000,
    )

    # ── F: DPO Preference Pairs ────────────────────────────────────
    build_dpo_pairs(
        sft_pairs,
        output_path="data/processed/dpo_pairs.jsonl",
        max_from_md2d=1000,
        max_from_shp2=1000,
    )

    # ── G: Evaluation Test Set ─────────────────────────────────────
    build_eval_test_set(
        dial_ds,
        span_index,
        output_path="data/processed/test_cases.jsonl",
        n_cases=200,
    )

    # ── Summary ────────────────────────────────────────────────────
    neg_types = Counter(
        ntype
        for t in all_triples
        for ntype in t.get("negative_types", ["same_doc"])
    )
    src_counts = Counter(t["source"] for t in all_triples)

    print("\n" + "=" * 60)
    print("  ✓ All training data built.")
    print("=" * 60)
    print(f"  Retriever triples : {len(all_triples):,}")
    print(f"    by source       : {dict(src_counts)}")
    print(f"    by neg type     : {dict(neg_types)}")
    print(f"  SFT pairs         : {len(sft_pairs):,}")
    print("=" * 60)
    print("  Next step: python -m src.retrieval.train_retriever --quick")


# ══════════════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════════════

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Merged training data builder — MD2D + Telecom"
    )
    p.add_argument("--skip_bm25",    action="store_true",
                   help="Disable BM25 hard-negative mining (faster but lower quality)")
    p.add_argument("--use_ce_gate",  action="store_true",
                   help="Enable cross-encoder quality gate (recommended but slower)")
    p.add_argument("--ce_margin",    type=float, default=1.0,
                   help="Minimum CE score gap (pos - neg) to keep triplet")
    p.add_argument("--save_splits",  action="store_true",
                   help="Also write train/val split files under data/processed/triplets/")
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    build_all_training_data(
        use_bm25    = not args.skip_bm25,
        use_ce_gate = args.use_ce_gate,
        ce_margin   = args.ce_margin,
        save_splits = args.save_splits,
    )