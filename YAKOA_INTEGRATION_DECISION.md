# Yakoa API Integration - Go/No-Go Decision Report

**Date**: Current Analysis  
**Decision Maker**: Senior System Architect  
**Project**: Companion Camp Backend - Hackathon Project

---

## 🎯 Executive Summary

**RECOMMENDATION: ❌ NO-GO**

**Reason**: Yakoa API is architecturally incompatible with pre-minting content verification workflow. The API requires blockchain identifiers (`contract_address`, `token_id`) that do not exist at Step 4 of our pipeline.

---

## 📋 Current Workflow Analysis

### Existing Pipeline (8 Steps)
```
1. Data Collection (X API: User Info + Tweet Scraping)
2. Ad Content Verification (Optional String Match)
3. Quantitative Data Check (Followers, Likes, Reposts)
4. [PROPOSED] Yakoa Plagiarism Check ← INSERTION POINT
5. AI Content Quality Check (Gemini API) ← EXPENSIVE STEP
6. Score Calculation & Contract Transaction
7. Contract Service (Token Transfer / Minting) ← MINTING HAPPENS HERE
8. Return Result
```

### Data Available at Step 4
- **Input**: Raw Web2 Tweet (text, images, metadata)
- **No Blockchain Data**: No `contract_address`, no `token_id`
- **Minting Status**: Pre-minting (happens at Step 7)

---

## 🔍 Technical Analysis

### 1. Yakoa API Requirements (from Documentation)

**Register Token Endpoint Requirements:**
- `contract_address` (mandatory) - Blockchain contract address
- `token_id` (mandatory) - Token identifier
- `image_url` (optional) - Content image
- `metadata` (optional) - Token metadata

**Critical Finding:**
- Yakoa's "Register Token" API is designed for **post-minting verification**
- It expects assets that **already exist on-chain**
- The API validates against its database of **registered IPs** (not general web)

### 2. Scope Verification

**Question**: Does Yakoa verify against general web or only minted IPs?

**Answer**: Based on documentation analysis:
- Yakoa checks against **registered IPs in its database**
- It distinguishes between:
  - `in_network_infringements`: Infringements within Yakoa's registered network
  - `external_infringements`: External IP violations (Brand owners)
- **NOT designed for general web scraping** (like Google Image Search)

### 3. Technical Feasibility Assessment

**Option A: Use Dummy Values**
```python
# Hypothetical implementation
yakoa_result = await yakoa_service.register_token(
    contract_address="0x0000000000000000000000000000000000000000",  # Dummy
    token_id="0",  # Dummy
    image_url=tweet_image_url,
    metadata={"tweet_id": tweet_id}
)
```

**Problems:**
1. ❌ **Invalidates Check Results**: Dummy values may cause API to reject or return invalid results
2. ❌ **No Pre-Minting Endpoint**: Yakoa doesn't provide a "check before minting" endpoint
3. ❌ **Database Mismatch**: Yakoa's database is for registered IPs, not raw content
4. ❌ **False Negatives**: May miss plagiarism if content isn't in Yakoa's database yet

**Option B: Post-Minting Check**
- Move Yakoa check to **Step 7** (after minting)
- **Problem**: Defeats the purpose (we want to filter BEFORE expensive AI call)

---

## 💰 Cost-Benefit Analysis

### Current Cost Structure
- **Step 4 (Proposed Yakoa)**: API call cost (unknown, likely free tier available)
- **Step 5 (Gemini AI)**: **EXPENSIVE** - Pay per API call
- **Goal**: Filter out plagiarism BEFORE Step 5 to save costs

### If Yakoa Integration Fails
- **Risk**: Run expensive Gemini API on plagiarized content
- **Mitigation**: Can implement simple text/image hash comparison as fallback

### If Yakoa Integration Succeeds (Unlikely)
- **Benefit**: Filter plagiarism before AI call
- **Reality**: Won't work due to architectural mismatch

---

## 🚨 Critical Blockers

### Blocker #1: Architectural Mismatch
- **Yakoa API**: Designed for post-minting verification
- **Our Need**: Pre-minting content verification
- **Impact**: Cannot use Yakoa at Step 4

### Blocker #2: Missing Data
- **Required**: `contract_address`, `token_id`
- **Available at Step 4**: None (minting happens at Step 7)
- **Impact**: Cannot satisfy API requirements

### Blocker #3: Scope Limitation
- **Yakoa Checks**: Only against registered IPs in database
- **Our Need**: General plagiarism detection
- **Impact**: May miss unregistered plagiarized content

---

## ✅ Alternative Solutions

### Option 1: Simple Hash-Based Duplicate Detection
```python
# Lightweight pre-filtering
def check_content_uniqueness(tweet_text, tweet_images):
    # Hash-based duplicate detection
    content_hash = hash(tweet_text + image_urls)
    # Check against local database of processed content
    return is_unique(content_hash)
```
**Pros**: Fast, cheap, works pre-minting  
**Cons**: Only detects exact duplicates, not similar content

### Option 2: Post-Minting Yakoa Check (Step 7)
- Move Yakoa check to after minting
- **Pros**: Uses Yakoa correctly
- **Cons**: Doesn't save Gemini API costs

### Option 3: Skip Yakoa Entirely
- Rely on Gemini AI for content quality (which may catch some plagiarism)
- **Pros**: Simplest, no integration overhead
- **Cons**: May process plagiarized content through expensive AI

---

## 📊 Decision Matrix

| Criteria | Yakoa Integration | Alternative (Hash Check) | Skip Yakoa |
|----------|------------------|-------------------------|------------|
| **Technical Feasibility** | ❌ No (architectural mismatch) | ✅ Yes | ✅ Yes |
| **Cost Savings** | ❓ Unknown (won't work) | ✅ Yes (lightweight) | ❌ No |
| **Plagiarism Detection** | ❓ Limited (only registered IPs) | ⚠️ Basic (exact matches) | ⚠️ Indirect (via AI) |
| **Implementation Time** | ❌ High (hackathon constraint) | ✅ Low | ✅ None |
| **Risk Level** | 🔴 High (may not work) | 🟢 Low | 🟢 Low |

---

## 🎯 Final Recommendation

### ❌ NO-GO for Yakoa Integration at Step 4

**Rationale:**
1. **Architectural Incompatibility**: Yakoa requires blockchain identifiers that don't exist pre-minting
2. **Time Constraint**: Hackathon deadline doesn't allow for API redesign
3. **Uncertain Value**: Even if integrated, may not catch all plagiarism (only registered IPs)
4. **High Risk**: Integration may fail or return invalid results

### ✅ Recommended Action Plan

**Short-term (Hackathon):**
1. **Implement simple hash-based duplicate detection** at Step 4
2. **Skip Yakoa integration** for now
3. **Document limitation** in demo presentation

**Long-term (Post-Hackathon):**
1. Evaluate Yakoa integration at **Step 7** (post-minting)
2. Consider alternative plagiarism detection services (e.g., Copyscape, PlagiarismChecker)
3. Build custom image similarity detection using ML models

---

## 📝 Implementation Recommendation

### Immediate Action: Add Lightweight Pre-Filter

```python
# app/services/plagiarism_service.py (NEW)
class PlagiarismService:
    def __init__(self):
        self.processed_hashes = set()  # In-memory cache
    
    async def check_content_uniqueness(self, tweet_text: str, image_urls: list) -> dict:
        """
        Lightweight duplicate detection using content hashing
        Returns: {"is_unique": bool, "reason": str}
        """
        # Create content hash
        content_string = tweet_text + "|".join(image_urls)
        content_hash = hashlib.sha256(content_string.encode()).hexdigest()
        
        # Check against processed content
        if content_hash in self.processed_hashes:
            return {
                "is_unique": False,
                "reason": "Exact duplicate content detected"
            }
        
        # Add to processed set
        self.processed_hashes.add(content_hash)
        return {
            "is_unique": True,
            "reason": "Content appears unique"
        }
```

**Integration Point**: Insert at Step 4 in `app/api/evaluation.py`

---

## 🔚 Conclusion

**Yakoa API integration is NOT feasible for pre-minting content verification** due to architectural constraints. The API is designed for post-minting IP protection, not pre-minting plagiarism detection.

**Recommendation**: Implement lightweight hash-based duplicate detection as a cost-saving measure, and skip Yakoa integration for the hackathon timeline.

---

**Decision Status**: ❌ **NO-GO**  
**Next Steps**: Implement alternative plagiarism detection (hash-based)  
**Risk Level**: 🟢 **LOW** (no integration risk, simple fallback)

