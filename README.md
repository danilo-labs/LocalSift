<div align="center">

# LocalSift

**The Ultra-lightweight, Offline RAG for Low-Spec PCs.**
No Docker. No Vector DB. No Node.js. Just pure Python + BM25 + Vanilla JS.

![License](https://img.shields.io/badge/license-MIT-blue)
![Version](https://img.shields.io/badge/version-v1.1.1-8b5cf6)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![No Docker](https://img.shields.io/badge/Docker-0%25-success)

</div>

---

**Ask questions about your documents. Everything runs on your machine — no cloud, no accounts, no data leaving your device.**

Why choose LocalSift?
*   🪶 **Featherweight:** Runs on a 4GB RAM laptop. Extraction happens in memory.
*   🔒 **Privacy-First:** 100% offline. Connects only to local LLMs (Ollama/KoboldCpp) via `127.0.0.1`.
*   🧠 **Smart Retrieval:** Uses a custom BM25 algorithm in pure JS instead of heavy Vector Databases.
*   🎯 **Relative Filtering:** Automatically discards irrelevant document chunks that fall below 50% of the best BM25 score.
*   📄 **Multi-format:** Reads PDF, ODT, DOCX, TXT, MD, CSV.

---

## 🚀 Quick Start

1. **Download the latest release** `LocalSift-v1.1.1.zip` from the [Releases page](https://github.com/danilo-labs/LocalSift/releases/latest) and extract it.
2. **Start Ollama** (or KoboldCpp) on your machine.
3. **Run LocalSift**: 
   - Double-click `LocalSift.desktop` (Linux)
   - Or run `bash start_localsift.sh` in your terminal.
4. **Open your browser** at `http://127.0.0.1:8200/index.html`.

## 🛠 How it works
1. **Upload:** The Python backend extracts text from your files using standard libraries (and `pypdf`).
2. **Search:** The frontend uses BM25 to find the most relevant paragraphs.
3. **Filter:** Only the fragments that score above the relative threshold are passed to the AI.
4. **Generate:** The local LLM answers using *only* the provided context, with strict anti-hallucination guardrails.

## 📋 Requirements
- Linux (or any OS with Python 3 and a web browser)
- Python 3.8+
- [Ollama](https://ollama.com/) or [KoboldCpp](https://github.com/LostRuins/koboldcpp) running locally.

## 🤝 Contributing
Issues and pull requests are welcome! Please check the `.github` folder for templates. Multilingual documentation improvements are especially appreciated.
