# 🧠 Car Clinic Smart Repair Advisor 🚗🛠️

A fully autonomous, LLM-powered data pipeline that extracts real-world automotive problems from Reddit, cleans, structures, augments, and tags them, then intelligently recommends the most appropriate Car Clinic repair branch using semantic similarity, tags, and location. The system culminates in a real-time LLM-powered Emergency Repair Assistant for customers and mechanics.

---

## 📌 Table of Contents

- [🔎 Project Overview](#-project-overview)
- [🚀 Final Goals](#-final-goals)
- [🏁 Competitors](#-competitors)
- [⚠️Challenges Faced](#-challenges-faced)
- [⛔ Project Roadblocks](#-project-roadblocks)
- [💡 Suggested Solution](#-suggested-solution)
- [📈 System Architecture](#-system-architecture)
- [🛠️ Features](#️-features)
- [🧪 Pipeline Phases](#-pipeline-phases)
- [🧬 Data Flow Diagram](#-data-flow-diagram)
- [🗂 Directory Structure](#-directory-structure)
- [⚙️ Tech Stack](#️-tech-stack)
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

## ⚠️ Challenges Faced

- **Data Noise and Quality**: Reddit data contains spam, bot posts, slang, and irrelevant content making cleaning complex.  
- **LLM Offline Processing**: Running large language models locally for data cleaning and understanding requires significant compute and optimization.  
- **Tagging Consistency**: Creating a comprehensive yet manageable tag schema for diverse car issues and mechanic specialties is difficult.  
- **Semantic Matching Accuracy**: Aligning user problems with correct branches involves fine-tuning embeddings and filter heuristics.  
- **Multilingual and Slang Variations**: Handling multiple languages and informal expressions adds complexity to augmentation and translation.  
- **Integration Complexity**: Combining multiple phases—data extraction, cleaning, tagging, embedding, recommendation, and chatbot—requires robust orchestration.

---
