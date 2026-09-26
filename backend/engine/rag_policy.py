"""
Medical Policy RAG Pipeline
FAISS vector search over embedded health policy documents.
Returns matched policy clauses for underwriter review.
"""

import logging
import threading
import numpy as np

logger = logging.getLogger(__name__)

_index = None
_chunks = None
_embedder = None
_ready = False          # True once index is fully built
_build_lock = threading.Lock()


POLICY_DOCUMENTS = [
    ("Waiting Period", "A waiting period of 30 days applies to all new policies before any outpatient claims can be submitted. Inpatient claims have a 90-day waiting period for pre-existing conditions."),
    ("Pre-existing Conditions", "Pre-existing conditions diagnosed within 12 months prior to policy inception are excluded from coverage during the first policy year. Disclosure of pre-existing conditions is mandatory at underwriting."),
    ("Inpatient Cover", "Inpatient hospitalization is covered up to KES 2,000,000 per annum. The benefit includes accommodation, surgical procedures, anesthesia, and specialist consultations during admission."),
    ("Outpatient Cover", "Outpatient benefits are limited to KES 50,000 per annum and cover general practitioner consultations, diagnostic tests, and prescribed medications."),
    ("Maternity Benefit", "Maternity cover commences after a 10-month waiting period. Normal delivery is covered up to KES 80,000 and caesarean section up to KES 150,000."),
    ("Chronic Illness Management", "Members diagnosed with chronic conditions such as diabetes mellitus, hypertension, or asthma qualify for the Chronic Disease Management Program with an additional benefit of KES 30,000 per annum."),
    ("Fraud and Misrepresentation", "Any fraudulent claim, misrepresentation of medical history, or submission of falsified documents shall result in immediate policy cancellation and potential legal action under Section 47 of the Insurance Act."),
    ("Claims Submission", "All claims must be submitted within 90 days of the date of service. Claims submitted after this period will be declined unless supported by documented evidence of extenuating circumstances."),
    ("Exclusions - General", "This policy does not cover cosmetic surgery, experimental treatments, dental treatment unless resulting from accidental injury, self-inflicted injuries, or treatment required as a result of war or civil unrest."),
    ("Premium Loading for High Risk", "Applicants classified as High Risk following underwriting assessment are subject to premium loading of up to 150%. The underwriter reserves the right to apply additional exclusion riders for specific conditions."),
    ("Renewal Terms", "Policies are renewable annually. The insurer reserves the right to revise premium rates at renewal based on claims experience. A no-claims discount of 10% applies if no claims were made in the preceding year."),
    ("ICD-10 Diabetes Codes", "Diabetes mellitus type 1 (E10), Diabetes mellitus type 2 (E11), and gestational diabetes (O24) are classified as chronic conditions under this policy and qualify for chronic disease management benefits."),
    ("ICD-10 Cardiovascular Codes", "Essential hypertension (I10), Ischemic heart disease (I20-I25), Heart failure (I50), and Cerebrovascular disease (I60-I69) are subject to specialized underwriting review for high-risk classification."),
    ("Subrogation Rights", "The insurer retains the right of subrogation in respect of any claim paid under this policy. The insured must cooperate in recovery proceedings against liable third parties."),
    ("IBNR Reserve Policy", "The company maintains Incurred But Not Reported (IBNR) reserves calculated using the Chain-Ladder development method applied to quarterly claims triangles. Reserve adequacy is reviewed semi-annually by the appointed actuary."),
]


def _get_model():
    global _embedder
    if _embedder is None:
        from sentence_transformers import SentenceTransformer
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder


def _build_index():
    global _index, _chunks, _ready
    import faiss

    with _build_lock:
        if _ready:          # another thread may have finished while we waited
            return
        logger.info("RAG: loading sentence-transformer model...")
        model = _get_model()
        _chunks = POLICY_DOCUMENTS

        texts = [f"{title}: {text}" for title, text in _chunks]
        logger.info("RAG: encoding %d policy documents...", len(texts))
        embeddings = model.encode(texts, convert_to_numpy=True).astype("float32")

        # L2-normalize for cosine similarity via inner product
        faiss.normalize_L2(embeddings)

        dim = embeddings.shape[1]
        _index = faiss.IndexFlatIP(dim)
        _index.add(embeddings)
        _ready = True
        logger.info("RAG: index ready — %d vectors, dim=%d", len(texts), dim)


def preload():
    """Call this at server startup to build the index in a background thread."""
    t = threading.Thread(target=_build_index, daemon=True, name="rag-preload")
    t.start()
    return t


def query_policy(query: str, top_k: int = 3) -> dict:
    """
    Search policy documents for clauses relevant to the query.

    Args:
        query: natural language query from underwriter
        top_k: number of results to return (default 3)

    Returns:
        query, matched_clauses (list of clause + source + score), top_match
    """
    import faiss

    global _index, _chunks
    if not _ready:
        # Still warming up — build synchronously (only happens if request arrives
        # before the background preload thread has finished)
        _build_index()

    model = _get_model()
    query_vec = model.encode([query], convert_to_numpy=True).astype("float32")
    faiss.normalize_L2(query_vec)

    scores, indices = _index.search(query_vec, top_k)

    matched_clauses = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < len(_chunks):
            title, text = _chunks[idx]
            matched_clauses.append({
                "clause": text,
                "source": title,
                "similarity_score": round(float(score), 4),
            })

    top_match = matched_clauses[0]["clause"] if matched_clauses else "No matching policy clause found."

    return {
        "query": query,
        "matched_clauses": matched_clauses,
        "top_match": top_match,
    }
