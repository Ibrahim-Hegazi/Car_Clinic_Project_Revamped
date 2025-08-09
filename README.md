# 🧠 Car Clinic Smart Repair Advisor 🚗🛠️

A fully autonomous, LLM-powered data pipeline that extracts real-world automotive problems from Reddit, cleans, structures, augments, and tags them, then intelligently recommends the most appropriate Car Clinic repair branch using semantic similarity, tags, and location. The system culminates in a real-time LLM-powered Emergency Repair Assistant for customers and mechanics.

---

## 📌 Table of Contents

- [🔎 Project Overview](#-project-overview)
- [🚀 Final Goals](#-final-goals)
- [🏁 Competitors](#-competitors)
- [❗ Challenges Faced](#-challenges-faced)
- [⛔ Project Roadblocks](#-project-roadblocks)
- [💡 Suggested Solutions](#-suggested-solutions)
- [📈 System Architecture](#-system-architecture)
- [🛠️ Features](#-features)
- [🧪 Pipeline Phases](#-pipeline-phases)
- [🧬 Data Flow Diagram](#-data-flow-diagram)
- [🗂 Directory Structure](#-directory-structure)
- [⚙️ Tech Stack](#-tech-stack)
- [⚡ Getting Started](#-getting-started)
- [🧠 Prompt Engineering Principles](#-prompt-engineering-principles)
- [🗓 Roadmap](#-roadmap)
- [🧾 License](#-license)
- [👨‍💻 Author](#-author)
- [📬 Future Improvements](#-future-improvements)
- [🙋‍♂️ Contributing](#-contributing)
- [📞 Contact](#-contact)

---

## 🔎 Project Overview

**Car Clinic Smart Repair Advisor** is an intelligent, modular system that reads thousands of Reddit threads from car repair subreddits, cleans and structures the data using LLMs, augments and tags content, and then recommends the best-fit repair branch using semantic similarity, embeddings, and geographic filters.

This enables:  
- ⚙️ Real-time, explainable repair suggestions  
- 🤖 LLM inference  
- 🌍 Multilingual data augmentation and understanding  
- 🧭 Nearest optimal repair branch recommendations  
- 💬 An interactive chatbot interface for customers and mechanics  

---

## 🚀 Final Goals

- ✅ Autonomous pipeline: From daily Reddit scraping to real-time recommendations.  
- ✅ LLM processing: Clean noisy car repair data into structured problem–solution pairs.  
- ✅ Semantic tagging and embeddings: Enrich issue understanding and enable vector similarity.  
- ✅ Smart Branch Recommender: Match user problems with the best nearby branch based on tags, embeddings, and availability.  
- ✅ Emergency LLM Chatbot: Provide instant fixes and guidance to mechanics and users in real-time.  
- ✅ API + CI/CD Ready: Modular FastAPI backend with GitHub Actions and Prefect orchestration.  
- ✅ Fully documented: Complete with data samples, diagrams, testing artifacts, and prompt design logic.

---

## 🏁 Competitors

Several projects and platforms tackle automotive problem diagnosis and repair recommendations using AI and data-driven approaches. Notable competitors include:

- **[RepairPal](https://repairpal.com/)**: Offers cost estimates and nearby repair shops but lacks real-time AI-based issue parsing from community data.  
- **[YourMechanic](https://why.yourmechanic.com/)**: Provides on-demand mechanic services and diagnostics but doesn't leverage large-scale social data for problem insights.  
- **[CarMD](https://carmd.com/)**: Focuses on OBD-II diagnostic tools rather than community-driven repair advice.  
- **Open-source automotive chatbot projects**: Most lack integration with live community data sources (e.g., Reddit) and LLM Data Cleaning. Example Project: [car_maintenance_chatbot_project](https://github.com/zebmuhammad/car_maintenance_chatbot_project/tree/main)

---

## ❗ Challenges Faced

- **Data Noise and Quality**: Reddit data contains spam, bot posts, slang, and irrelevant content making cleaning complex.  
- **LLM Offline Processing**: Running large language models locally for data cleaning and understanding requires significant compute and optimization. Therefore leading to other solutions that might be costly.
- **Ollama-Based LLM Processing Time**: Current data cleaning with Ollama-based LLMs, while providing high-quality structured outputs, is time-intensive. For example, processing around 700 rows in Phase 2 can take approximately 31 hours to complete. This runtime presents a bottleneck for scaling and requires optimization or infrastructure improvements to achieve timely data processing.
- **Tagging Consistency**: Creating a comprehensive yet manageable tag schema for diverse car issues and mechanic specialties is difficult.  
- **Semantic Matching Accuracy**: Aligning user problems with correct branches involves fine-tuning embeddings and filter heuristics.  
- **Multilingual and Slang Variations**: Handling multiple languages and informal expressions adds complexity to augmentation and translation.  
- **Integration Complexity**: Combining multiple phases—data extraction, cleaning, tagging, embedding, recommendation, and chatbot—requires robust orchestration.

---

## ⛔ Project Roadblocks

- Limited computational resources for efficient offline LLM inference slowed data cleaning throughput.  
- Incomplete or evolving tag schemas caused misclassification in early testing phases.  
- Integration of real-time chatbot with backend recommender still in prototype stage, delaying deployment.  
- Dataset imbalance due to sparse comments or rare issues affected model generalization.  
- Ongoing challenges in automating end-to-end orchestration with retries and failure handling.

---


## 💡 Suggested Solutions

- **Optimize LLM Models**: Explore quantized models or smaller LLMs with comparable performance to speed up offline inference.
- **Refine Tagging Ontology**: Collaborate with domain experts to finalize tag schema and implement automated tag validation.  
- **Enhance Data Pipeline**: Implement advanced filters and anomaly detection to reduce noise upstream.  
- **Improve Chatbot Integration**: Develop and test API endpoints for seamless real-time interactions and expand frontend support.  
- **Expand Multilingual Support**: Integrate additional language models and fine-tune back-translation workflows.  
- **Robust Orchestration**: Extend Prefect flows with better logging, alerting, and retries to improve pipeline stability.  
- **User Feedback Loop**: Design mechanisms to collect user feedback for continuous model improvements and retraining.  
- **Cloud Deployment Planning**: Prepare for scalable deployment using containerization and managed cloud services.  

---

## 🧪 Pipeline Phases

<details>
<summary>✅ Phase 1: Reddit Data Extraction (Scraping)</summary>

- 🔁 **Inputs:**
  - List of subreddits
  - Reddit API credentials (via `praw`)
  - Configs (e.g., number of posts, filters)

- ⚙️ **Inside:**
  - Fetch top daily/weekly posts with comments
  - Remove posts with no comments
  - Filter spam/bot content
  - Save results in `/data/raw/` as JSON or CSV

- 🎯 **Purpose:**  
  Collect relevant raw text data (real-world issues and discussions) for downstream LLM processing.

- 🔁 **Used again in:**  
  Phase 2 (Cleaning), Phase 10 (Re-training or evaluation for LLMs)

- 📤 **Outputs:**  
  `/data/raw/reddit_posts_with_comments.json`

</details>

<details>
<summary>✅ Phase 2: Reddit Data Cleaning (LLM-Based)</summary>

- 🔁 **Inputs:**  
  - Raw Reddit posts + top comments  
  - LLM model (offline or Ollama)  
  - Prompt template

- ⚙️ **Inside:**  
  - Preprocessing: Remove bots, normalize text  
  - LLM Inference: Extract (problem → solution) pairs using prompts  
  - Postprocessing: JSON formatting, hallucination checks, null handling

- 🎯 **Purpose:**  
  Converts noisy internet content into clean problem–solution pairs for chatbot and tagging.

- 🔁 **Used again in:**  
  Phase 3 (Tag Generation), Phase 9 (LLM chatbot fine-tuning)

- 📤 **Outputs:**  
  `/data/cleaned/cleaned_problems_solutions.json`

</details>

<details>
<summary>🦑 Phase 3: Data Augmentation & Translation</summary>

- 🔁 **Inputs:**  
  - Cleaned problem–solution pairs  
  - NLPAug/TextAttack or offline LLMs for paraphrasing  
  - Optional translation APIs or offline models  
  - Noise injection rules (typos, slang)

- ⚙️ **Inside:**  
  - Paraphrasing: Generate 1–3 semantically similar versions  
  - Translation: Translate → Back-translate (e.g., EN → AR → EN)  
  - Noise Injection: Add typos, abbreviations  
  - Flow management: `augmenter/flow.py`, `translator/flow.py`

- 🎯 **Purpose:**  
  Increase data diversity and robustness to phrasing variability and multilingual input.

- 🔁 **Used again in:**  
  Phase 5 (Embedding generation), Phase 10 (Chatbot understanding)

- 📤 **Outputs:**  
  `/data/augmented/augmented_problems_solutions.json`

</details>

<details>
<summary>🌿 Phase 4: Tag Generator (Problem + Solution Tags)</summary>

- 🔁 **Inputs:**  
  - Cleaned or augmented problem–solution pairs  
  - Tagging rules or LLM model  
  - Optional keyword dictionaries or tag schemas

- ⚙️ **Inside:**  
  - Extract semantic tags from problems and solutions  
  - Track source (rule-based, LLM, or hybrid)  
  - Store metadata like confidence, LLM version  
  - Orchestrated via `tag_generator/flow.py`

- 🎯 **Purpose:**  
  Enables structured understanding for tag-based filtering and scoring in recommendations.

- 🔁 **Used again in:**  
  Phase 6 (Tag-based matching), Phase 10 (Chatbot explanations)

- 📤 **Outputs:**  
  `/data/tagged/tagged_problems_solutions.json`

</details>

<details>
<summary>🔢 Phase 5: Embedding Generation (Problems + Branches)</summary>

- 🔁 **Inputs:**  
  - Cleaned/tagged problem–solution pairs  
  - Branch expertise descriptions  
  - Pretrained embedding model (e.g., Sentence-BERT, Instructor-XL)

- ⚙️ **Inside:**  
  - Vectorize problem–solution pairs  
  - Vectorize branch expertise profiles  
  - Store embeddings separately (`/data/embeddings/problems/`, `/data/embeddings/branches/`)  
  - Auto-skip already embedded entries  
  - Freeze model versions & store hashes  
  - Flow handled by `embedding_generator/flow.py`

- 🎯 **Purpose:**  
  Enables similarity-based retrieval and matching for hybrid recommendations.

- 🔁 **Used again in:**  
  Phase 6 (Similarity scoring), Phase 10 (Chatbot reasoning)

- 📤 **Outputs:**  
  `/data/embeddings/problems/*.npy`, `/data/embeddings/branches/*.npy`

</details>

<details>
<summary>🗺️ Phase 6: Branch Recommender System</summary>

- 🔁 **Inputs:**  
  - Tagged problems  
  - Problem embeddings  
  - Branch embeddings + tag profiles  
  - Branch availability + location (optional)

- ⚙️ **Inside:**  
  - Match tags (e.g., Jaccard Index)  
  - Match vectors (cosine similarity)  
  - Apply location filter if coordinates provided  
  - Composite scoring: weighted formula of tags, embeddings, location  
  - Return top-N recommendations with explainability logs  
  - Flow: `branch_recommender/flow.py`

- 🎯 **Purpose:**  
  Core logic to choose the best-fit repair branch per user query.

- 🔁 **Used again in:**  
  Phase 10 (Chatbot resolution), Phase 11 (Backend endpoint)

- 📤 **Outputs:**  
  `/data/recommendations/top_branches_for_postid.json`

</details>

<details>
<summary>🧪 Phase 7: Local & Integrated Testing</summary>

- 🔁 **Inputs:**  
  - Outputs from previous phases  
  - Small manually crafted test batch  
  - Expected results/ground truth (if available)

- ⚙️ **Inside:**  
  - Run unit tests per script  
  - Run integration tests on test batch  
  - Visualize embeddings, matches, tags  
  - Store snapshots in `/docs/test_cases/`

- 🎯 **Purpose:**  
  Verify correctness and integration before scaling.

- 🔁 **Used again in:**  
  Phase 12 (Documentation), CI/CD (Phase 9)

- 📤 **Outputs:**  
  `/docs/test_cases/*.json`, `/docs/test_results/`, visuals

</details>

<details>
<summary>🌀 Phase 8: Prefect Orchestration</summary>

- 🔁 **Inputs:**  
  - All flow.py scripts (Phases 1–6)  
  - Prefect config (retry, logging)  
  - Optional Prefect Cloud credentials

- ⚙️ **Inside:**  
  - Convert scripts to Prefect tasks  
  - Chain tasks in logical order  
  - Add retries, error handlers, logging  
  - Trigger from CLI or schedule

- 🎯 **Purpose:**  
  Automate and connect pipeline parts in modular robust system.

- 🔁 **Used again in:**  
  Phase 9 (CI/CD), Phase 11 (Runtime scheduling)

- 📤 **Outputs:**  
  Prefect DAG, CLI runnable flows, logs

</details>

<details>
<summary>☁️ Phase 9: GitHub Actions & Deployment</summary>

- 🔁 **Inputs:**  
  - GitHub repo + workflows  
  - Prefect-compatible flows  
  - Secrets (.env or GitHub Secrets)

- ⚙️ **Inside:**  
  - Run flows (scraping, cleaning, tagging, embedding, matching)  
  - Scheduled daily (e.g., 12:15 PM Egypt time)  
  - Support matrix builds and parallelization  
  - Optional Docker container builds

- 🎯 **Purpose:**  
  Fully automated data ingestion & processing pipeline on GitHub infrastructure.

- 🔁 **Used again in:**  
  All phases (1–6), redeployment on code updates

- 📤 **Outputs:**  
  Daily updated `/data/`, GitHub CI logs, optional Docker images

</details>

<details>
<summary>📘 Phase 10: LLM Chatbot Engine</summary>

- 🔁 **Inputs:**  
  - User query (via REST API)  
  - Cleaned + tagged Reddit problems  
  - Embeddings (problems & branches)  
  - Branch metadata (tags, location)

- ⚙️ **Inside:**  
  - Classify query intent  
  - Retrieve similar Reddit cases  
  - LLM generates structured response  
  - Match to branch via Phase 6 logic  
  - Format JSON response for chatbot

- 🎯 **Purpose:**  
  Frontline AI interaction interface.

- 🔁 **Used again in:**  
  Phase 11 (API routes), Phase 12 (docs)

- 📤 **Outputs:**  
  Structured JSON `{ "solution": ..., "branch": ..., "confidence": ... }`

</details>

<details>
<summary>🚪 Phase 11: Backend Integration (FastAPI)</summary>

- 🔁 **Inputs:**  
  - Chatbot logic (Phase 10)  
  - Recommender logic (Phase 6)  
  - Processed data (embeddings, tags)  
  - API config & schema

- ⚙️ **Inside:**  
  - REST endpoints: `/chat/solve`, `/recommend/branch`  
  - Parse inputs, run logic, return JSON  
  - Dockerized for modular deployment  
  - Optional Redis caching

- 🎯 **Purpose:**  
  Expose system via API for production apps.

- 🔁 **Used again in:**  
  Real-time deployment, frontend integration

- 📤 **Outputs:**  
  `main.py` FastAPI server, OpenAPI docs

</details>

<details>
<summary>📘 Phase 12: Documentation & Finalization</summary>

- 🔁 **Inputs:**  
  - All code, flows, configs, data samples  
  - Testing results (Phase 7)  
  - Model & LLM choices

- ⚙️ **Inside:**  
  - Create README, architecture diagrams  
  - Document phases and modules  
  - Glossary, schema definitions  
  - Data samples & test outputs

- 🎯 **Purpose:**  
  Make pipeline shareable, reproducible, production-ready.

- 🔁 **Used again in:**  
  Onboarding, public release, presentations

- 📤 **Outputs:**  
  `/docs/`, `README.md`, diagrams, prompt designs, schema

</details>

