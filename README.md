# 🚀 DIDA - Domain-Aware Intelligent Data Scientist Agent

![DIDA Banner](https://img.shields.io/badge/DIDA-v1.0-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.9+-green?style=for-the-badge&logo=python)
![React](https://img.shields.io/badge/React-18+-61DAFB?style=for-the-badge&logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=for-the-badge&logo=fastapi)

**DIDA** is a multi-agent AI system that revolutionizes data science workflows by automatically understanding, cleaning, and analyzing datasets with human-like reasoning and domain awareness.

---

## ✨ Features

### 🎯 Core Capabilities

- **📊 Smart Dataset Upload** - Support for CSV, Excel, TSV, and paste data
- **🧠 AI-Powered Analysis** - Automatic schema understanding and semantic interpretation
- **🔍 Domain Awareness** - Infers business context and industry-specific insights
- **🧹 Intelligent Cleaning** - Human-like data cleaning decisions with explanations
- **⚙️ Feature Engineering** - Automatic creation of derived features
- **💬 Chat with Data** - Natural language queries on your dataset
- **📈 Visualizations** - Interactive charts and statistical summaries
- **📄 Professional Reports** - PDF and HTML reports with insights
- **🔐 Secure API Keys** - User-provided OpenAI keys (session-only storage)

### 🤖 Multi-Agent Architecture

1. **Schema Analyzer Agent** - Understands data structure and types
2. **Domain Knowledge Agent** - Applies business logic and domain rules
3. **Cleaning Reasoning Agent** - Makes intelligent cleaning decisions
4. **ML Engineer Agent** - Performs feature engineering and importance scoring
5. **Reporting Agent** - Generates comprehensive analysis reports
6. **Chat Agent** - Processes natural language queries

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│         Frontend (React + Vite)             │
│  • File Upload  • Data Preview  • Chat     │
│  • Analysis View  • Settings  • Reports    │
└─────────────────┬───────────────────────────┘
                  │ REST API
┌─────────────────┴───────────────────────────┐
│         Backend (FastAPI)                   │
│  • Upload  • Analyze  • Clean  • Chat      │
│  • Feature Engineering  • Export  • Auth   │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────┴───────────────────────────┐
│         Multi-Agent System                  │
│  OpenAI GPT-4 + Specialized Agents          │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────┴───────────────────────────┐
│    Data Processing Engine                   │
│  Pandas • Polars • Scikit-learn • Plotly   │
└─────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+**
- **Node.js 18+**
- **OpenAI API Key** (user-provided or system-level)

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/dida-agent.git
cd dida-agent
```

#### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env

# Edit .env and add your OpenAI API key (optional - users can provide their own)
# OPENAI_API_KEY=sk-your-key-here
```

#### 3. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install
```

### Running the Application

#### Start Backend (Terminal 1)

```bash
cd backend
python main.py
```

Backend will run on `http://localhost:8000`

#### Start Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

Frontend will run on `http://localhost:5173`

#### Access the Application

Open your browser and navigate to:
```
http://localhost:5173
```

---

## 📖 Usage Guide

### 1. Upload Your Dataset

- **Drag & Drop** a CSV, Excel, or TSV file
- **Browse Files** to select from your computer
- **Paste Data** directly into the text area

### 2. Configure API Key (if needed)

- Click the **Settings** icon (⚙️) in the header
- Enter your OpenAI API key
- The key is validated and stored in session memory only
- **Privacy**: Keys are never saved to disk or database

### 3. Analyze Your Data

- Click the **Analysis** tab
- AI automatically analyzes your dataset
- View insights about:
  - Column meanings and data types
  - Data quality issues
  - Suggested target variable
  - Domain-specific insights

### 4. Chat with Your Data

- Click the **Chat** tab
- Ask questions in natural language:
  - "Show me summary statistics"
  - "Plot the distribution of age"
  - "What are the top 5 categories?"
  - "Show correlation between features"

### 5. Export Results (Coming Soon)

- Download cleaned dataset
- Get Python code for reproducibility
- Export Jupyter notebook template

---

## 🛠️ API Endpoints

### Authentication

- `POST /api/auth/set-key` - Validate and set OpenAI API key
- `DELETE /api/auth/remove-key` - Remove session API key
- `GET /api/auth/key-status` - Check key availability

### Data Operations

- `POST /api/upload/file` - Upload CSV/Excel/TSV file
- `POST /api/upload/paste` - Upload pasted data
- `POST /api/analyze/` - Analyze dataset with AI
- `POST /api/clean/` - Clean dataset (Coming Soon)
- `POST /api/feature-engineering/` - Engineer features (Coming Soon)
- `POST /api/chat/` - Chat with dataset (Coming Soon)
- `POST /api/report/generate` - Generate report (Coming Soon)
- `POST /api/export/` - Export results (Coming Soon)

---

## 🔒 Security & Privacy

### API Key Management

- ✅ User keys stored in **session memory only**
- ✅ Keys **never persisted** to disk or database
- ✅ Keys cleared when browser session ends
- ✅ All requests made directly to OpenAI
- ✅ Optional system-level fallback key

### Data Privacy

- Your data is processed locally on your server
- No data is sent to third parties except OpenAI for AI processing
- Uploaded files are stored temporarily in session directories
- You can delete session data at any time

---

## 🎨 Tech Stack

### Frontend

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **TailwindCSS** - Utility-first CSS
- **Zustand** - State management
- **Axios** - HTTP client
- **Plotly.js** - Interactive visualizations
- **Lucide React** - Icon library

### Backend

- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **Pandas/Polars** - Data manipulation
- **Scikit-learn** - ML utilities
- **OpenAI API** - GPT-4 integration
- **Plotly/Matplotlib** - Visualizations
- **ReportLab** - PDF generation

---

## 🗺️ Roadmap

### ✅ MVP (Current)

- [x] File upload and preview
- [x] AI-powered schema analysis
- [x] OpenAI key management
- [x] Basic chat interface
- [x] Premium UI design

### 🚧 In Progress

- [ ] Data cleaning with AI reasoning
- [ ] Feature engineering
- [ ] Report generation (PDF/HTML)
- [ ] Full chat functionality with visualizations
- [ ] Export cleaned data and code

### 🔮 Future

- [ ] SQL database connectors
- [ ] Multi-model LLM support (Groq, Gemini, Anthropic)
- [ ] Automated Jupyter notebook generation
- [ ] Dataset comparison view
- [ ] Collaborative features
- [ ] Advanced visualization dashboard
- [ ] Custom domain rules editor

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Vimalathas Vithusan**

- Project: DIDA v1.0
- Built with ❤️ using React, FastAPI, and OpenAI GPT-4

---

## 🙏 Acknowledgments

- OpenAI for GPT-4 API
- FastAPI community
- React and Vite teams
- All open-source contributors

---

## 📧 Support

For issues, questions, or suggestions:

- Open an issue on GitHub

---

<div align="center">

**⭐ Star this repo if you find it useful! ⭐**

Made with 🤖 AI and ❤️ Human creativity

</div>