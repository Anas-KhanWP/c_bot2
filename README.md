# 🧙‍♂️ Querymancer

> *Your AI Database Assistant - Transform natural language into database insights*

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/LangChain-Latest-green.svg)](https://langchain.com)

## ✨ Features

- 🤖 **AI-Powered Queries** - Ask questions in natural language
- 🔍 **Smart Database Exploration** - Automatically discovers table structures
- 📊 **Rich Data Visualization** - Clean tables and formatted results
- 🛡️ **Read-Only Safety** - Protected against data modifications
- 🚀 **Multiple AI Providers** - Support for Ollama and Groq models
- 💬 **Interactive Chat Interface** - Streamlit-powered web UI

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Ollama (optional) or Groq API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Anas-KhanWP/c_bot2.git
   cd c_bot2
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Create .env file
   GROQ_API_KEY=your_groq_api_key_here
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

## 🏗️ Project Structure

```
c_bot2/
├── 🎯 app.py                 # Main Streamlit application
├── 📁 querymancer/           # Core package
│   ├── 🤖 agent.py          # AI agent logic
│   ├── ⚙️ config.py         # Configuration settings
│   ├── 📝 logging.py        # Logging utilities
│   ├── 🧠 models.py         # AI model providers
│   └── 🛠️ tools.py          # Database tools
├── 📊 data/                  # Database files
│   └── ecommerce.sqlite      # Sample database
├── 🎨 assets/                # Static assets
│   └── style.css             # Custom styles
└── 📋 requirements.txt       # Dependencies
```

## 🔧 Configuration

### AI Models

Choose your preferred AI provider in `querymancer/config.py`:

```python
# Available models
QWEN_2_5 = ModelConfig("qwen2.5", ModelProvider.OLLAMA, 0.1)
GEMMA_3 = ModelConfig("PetroStav/gemma3-tools:12b", ModelProvider.OLLAMA, 0.7)
LLAMA_3_3 = ModelConfig("llama-3.3-70b-versatile", ModelProvider.GROQ, 0.0)

# Set active model
MODEL_CONFIG = QWEN_2_5  # Using Groq by default
```

### Database

The application comes with a sample ecommerce database containing:
- 👥 **customers** - Customer information
- 📦 **products** - Product catalog
- 🛒 **orders** - Order records
- 📋 **order_items** - Order line items

## 💡 Usage Examples

### Basic Queries
- *"How many customers do we have?"*
- *"What are our top-selling products?"*
- *"Show me recent orders"*

### Complex Analysis
- *"Which customers have spent the most money?"*
- *"What's the average order value by country?"*
- *"Show me product performance by category"*

## 🛡️ Safety Features

- ✅ **Read-only operations** - No data modifications allowed
- ✅ **SQL injection protection** - Parameterized queries
- ✅ **Query validation** - Blocks harmful operations
- ✅ **Error handling** - Graceful failure management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io) for the web interface
- Powered by [LangChain](https://langchain.com) for AI orchestration
- Uses [Rich](https://rich.readthedocs.io) for beautiful console output

---

<div align="center">
  <strong>Made with ❤️ for the data community</strong>
</div>