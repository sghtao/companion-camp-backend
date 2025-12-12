# Yakoa API Search Capability Analysis
## Pre-Minting Content Verification Feasibility Study

**Date**: Current Analysis  
**Question**: Can Yakoa API perform "Reverse Content Search" (Raw Content → Match Detection) BEFORE minting?

---

## 🎯 Your Question: Scenario A vs Scenario B

### Scenario A (What You Need): "Content Search Engine"
```
Input: Raw Text/Image URL
Output: "Match Found in Yakoa DB" (Yes/No + Details)
Use Case: Check BEFORE minting to prevent duplicates
```

### Scenario B (What Yakoa Provides): "Registry Lookup"
```
Input: contract_address + token_id (Blockchain Identifiers)
Output: "Infringement Status of THIS specific token"
Use Case: Check AFTER minting to verify registered IP
```

---

## 🔍 Technical Analysis: Yakoa API Architecture

### 1. Yakoa's Core Workflow (From Documentation)

Based on the Key Concepts documentation:

```
Step 1: Register Token
  ├─ Requires: contract_address (mandatory)
  ├─ Requires: token_id (mandatory)
  ├─ Optional: media URLs (images, videos, audio)
  └─ Optional: metadata
  ↓
Step 2: Yakoa Performs Infringement Check
  ├─ Checks against: Registered IPs in Yakoa database
  ├─ Checks against: Brand IP (external_infringements)
  └─ Checks against: In-network IPs (in_network_infringements)
  ↓
Step 3: Get Results
  ├─ Query by: contract_address + token_id
  └─ Returns: Infringement status, matches, details
```

### 2. Critical Finding: No "Pre-Registration" Endpoint

**Key Observation:**
- Yakoa's API is designed as a **"Register → Check → Query"** workflow
- There is **NO endpoint** that accepts raw content without blockchain identifiers
- The `Register Token` endpoint **requires** `contract_address` and `token_id`

### 3. API Endpoint Analysis

#### Register Token Endpoint (Hypothetical Structure)
```http
POST /api/v1/tokens/register
{
  "contract_address": "0x...",  // MANDATORY - Blockchain address
  "token_id": "123",             // MANDATORY - Token identifier
  "media": [                      // Optional - Content URLs
    {
      "url": "https://...",
      "type": "image"
    }
  ],
  "metadata": {}                  // Optional - Additional data
}
```

**Problem**: Cannot call this without `contract_address` and `token_id` (which don't exist pre-minting)

#### Get Token Endpoint (Hypothetical Structure)
```http
GET /api/v1/tokens/{contract_address}/{token_id}
```

**Returns**: Infringement status of **this specific registered token**

**Problem**: Requires token to be registered first (post-minting)

---

## 📊 Direct Answer to Your Questions

### Q1: Can I initiate an infringement check using ONLY raw content (without contract_address or token_id)?

**Answer: ❌ NO**

**Reasoning:**
1. **API Design**: Yakoa's API requires blockchain identifiers (`contract_address`, `token_id`) as mandatory parameters
2. **No Content-Only Endpoint**: There is no endpoint that accepts raw content (text/image) without blockchain identifiers
3. **Workflow Dependency**: The infringement check is triggered **during** token registration, not before

**Evidence from Documentation:**
- Token registration requires `contract_address` and `token_id`
- Media URLs are optional, but the check is performed **on registered tokens**
- The system is designed for **post-minting verification**, not pre-minting content search

### Q2: If the API strictly requires contract_address to start any check, does this mean it is impossible to check for infringement before minting?

**Answer: ✅ YES - It is architecturally impossible**

**Reasoning:**
1. **Mandatory Parameters**: `contract_address` and `token_id` are required to initiate any check
2. **No Workaround**: There is no "pre-registration" or "content-only" endpoint
3. **Design Philosophy**: Yakoa is designed for **IP protection of minted assets**, not pre-minting content discovery

**Implications:**
- You **cannot** use Yakoa API at Step 4 (pre-minting)
- You **can** use Yakoa API at Step 7 (post-minting), but this defeats your cost-saving goal

---

## 🔬 Yakoa: Content Search Engine vs Registry Lookup

### Classification: **Registry Lookup (Scenario B)**

**Evidence:**

1. **Input Requirements**
   - Requires blockchain identifiers (contract_address, token_id)
   - Content (media URLs) is optional metadata
   - Cannot query without blockchain context

2. **Database Scope**
   - Checks against **registered IPs** in Yakoa's database
   - Checks against **Brand IP** (external IP owners who registered)
   - Does **NOT** search the general web (like Google Image Search)

3. **Use Case**
   - Designed for: "Is this minted token infringing on registered IP?"
   - NOT designed for: "Does this raw content exist anywhere?"

4. **Workflow**
   - Post-minting verification
   - Registry-based lookup
   - Token-centric (not content-centric)

### Comparison Table

| Feature | Content Search Engine (Scenario A) | Registry Lookup (Scenario B) |
|---------|-----------------------------------|------------------------------|
| **Input** | Raw content (text/image) | Blockchain identifiers |
| **Search Scope** | General web + databases | Registered IPs only |
| **Pre-Minting** | ✅ Yes | ❌ No |
| **Post-Minting** | ✅ Yes | ✅ Yes |
| **Example** | Google Image Search | Yakoa API |

**Yakoa = Scenario B (Registry Lookup)**

---

## 🚨 Critical Limitations for Your Use Case

### Limitation #1: No Pre-Minting Support
- **Problem**: Cannot check content before minting
- **Impact**: Cannot filter plagiarism before expensive AI call (Step 5)

### Limitation #2: Database Scope
- **Problem**: Only checks against registered IPs in Yakoa database
- **Impact**: May miss plagiarism if:
  - Content is plagiarized but not registered in Yakoa
  - Content exists on web but not in Yakoa's database
  - Content is from sources outside Yakoa's network

### Limitation #3: Architectural Mismatch
- **Problem**: API designed for post-minting verification
- **Impact**: Cannot integrate at Step 4 (pre-minting stage)

---

## 💡 What Yakoa CAN Do (Post-Minting)

If you move Yakoa check to **Step 7** (after minting):

### ✅ Feasible Workflow
```
Step 7: Mint Token
  ↓
Step 7.5: Register Token with Yakoa
  ├─ contract_address: From minting transaction
  ├─ token_id: From minting transaction
  ├─ media: Tweet image URLs
  └─ metadata: Tweet text, username, etc.
  ↓
Step 7.6: Query Infringement Status
  ├─ GET /tokens/{contract_address}/{token_id}
  └─ Returns: Infringement matches, status
```

**Pros:**
- Uses Yakoa correctly (as designed)
- Can detect infringement against registered IPs

**Cons:**
- ❌ **Doesn't save Gemini API costs** (AI call already happened at Step 5)
- ❌ **Too late** - Content already processed through expensive pipeline
- ❌ **Doesn't prevent** duplicate minting (only detects after minting)

---

## 🎯 Final Verdict

### Question: Is Yakoa a "Content Search Engine" (Scenario A) or "Registry Lookup" (Scenario B)?

**Answer: Yakoa is a "Registry Lookup" (Scenario B)**

### Question: Can we check for infringement BEFORE minting?

**Answer: ❌ NO - Architecturally impossible**

### Question: Should we integrate Yakoa at Step 4?

**Answer: ❌ NO-GO**

**Reasoning:**
1. Yakoa requires blockchain identifiers that don't exist pre-minting
2. No content-only search endpoint exists
3. Designed for post-minting IP protection, not pre-minting content discovery
4. Database scope limited to registered IPs (not general web)

---

## ✅ Recommended Alternatives

### Option 1: Lightweight Hash-Based Duplicate Detection (Recommended)
```python
# Check for exact duplicates before AI call
def check_content_uniqueness(tweet_text, image_urls):
    content_hash = hash(tweet_text + "|".join(image_urls))
    # Check against local database of processed content
    return is_unique(content_hash)
```
**Pros**: Fast, cheap, works pre-minting  
**Cons**: Only detects exact duplicates

### Option 2: Post-Minting Yakoa Check
- Move to Step 7 (after minting)
- **Pros**: Uses Yakoa correctly
- **Cons**: Doesn't save costs, too late to prevent duplicates

### Option 3: Alternative Plagiarism Detection Services
- **Copyscape API**: Text plagiarism detection
- **Google Vision API**: Image similarity search
- **TinEye API**: Reverse image search
- **Pros**: May support pre-minting checks
- **Cons**: Different APIs, different costs, different integration

---

## 📝 Conclusion

**Yakoa API is NOT a "Content Search Engine"** - it is a **"Registry Lookup"** system designed for post-minting IP protection.

**For your use case (pre-minting infringement check):**
- ❌ **Not feasible** with Yakoa API
- ✅ **Alternative solutions** required (hash-based detection or other services)

**Recommendation**: Skip Yakoa integration for pre-minting checks. Implement lightweight duplicate detection instead.

---

**Decision**: ❌ **NO-GO for Pre-Minting Integration**  
**Classification**: Yakoa = **Registry Lookup (Scenario B)**, NOT Content Search Engine  
**Alternative**: Hash-based duplicate detection or other plagiarism services

