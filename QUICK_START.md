# Harrison's Medical RAG - Quick Start Guide

## 🚀 Interactive Search (Terminal)

Test your RAG system with natural language queries from the command line!

### Start the Interactive Search:

```bash
cd "/Users/maayan/medicinal rag/backend"
source venv/bin/activate
python interactive_search.py
```

### How It Works:

1. **Ask a Question** in natural language
   ```
   🔍 Your question: what is the workup for hyponatremia
   ```

2. **See Results** from Harrison's
   ```
   📊 Found 5 relevant sections:
   
   [1] 53 Fluid and Electrolyte Disturbances
       📄 Pages: 1383-1448
       📈 Relevance: -0.212
       💬 Preview...
   
   [2] SECTION 7 Alterations in Renal...
       📄 Pages: 1334
       ...
   ```

3. **Select a Topic**
   ```
   👉 Select a result [1-5]: 1
   ```

4. **Get Page Numbers**
   ```
   ✅ SELECTED TOPIC
   📚 Topic: 53 Fluid and Electrolyte Disturbances
   📄 Pages: 1383 to 1448
   
   🎯 ACTION: Open Harrison's PDF to pages 1383-1448
   ```

### Example Queries:

**Cardiology:**
- "acute myocardial infarction management"
- "atrial fibrillation rate control"
- "heart failure treatment"

**Infectious Disease:**
- "pneumonia antibiotic selection"
- "septic shock management"
- "HIV treatment guidelines"

**Endocrinology:**
- "diabetes type 2 management"
- "thyroid storm treatment"
- "diabetic ketoacidosis workup"

**Nephrology:**
- "acute kidney injury causes"
- "hyponatremia workup"
- "hyperkalemia treatment"

**Oncology:**
- "basal cell carcinoma treatment"
- "melanoma staging"
- "breast cancer screening"

### Commands:

- Type your question naturally
- Type `q` to search again without selecting
- Type `quit` or `exit` to close
- Press `Ctrl+C` to exit anytime

---

## 🧪 Run Demo (Non-Interactive):

Test with a single query:

```bash
python demo_search.py
```

---

## ✅ What's Working:

1. ✅ **All 550 topics indexed** (20 Parts, 492 Chapters)
2. ✅ **Semantic search** - understands medical terminology
3. ✅ **Natural language queries** - ask questions normally
4. ✅ **Page number retrieval** - exact location in Harrison's
5. ✅ **Table & figure references** - knows what's in each section

---

## 📊 System Status:

- **Vector Database:** ChromaDB (local)
- **Embeddings:** OpenAI text-embedding-3-large (3,072 dimensions)
- **Documents:** 550 searchable topics
- **Coverage:** Entire Harrison's 21st Edition (15,164 pages)

---

## 🎯 Next Steps:

1. **Test various queries** to validate search quality
2. **Note any issues** with relevance or results
3. **Ready for:** FastAPI backend → Apple Watch app

---

## 🐛 Troubleshooting:

**"ModuleNotFoundError":**
```bash
source venv/bin/activate
```

**"Collection not found":**
```bash
python vector_store.py  # Re-index
```

**Poor results:**
- Try rephrasing your query
- Use medical terminology
- Be specific about what you're looking for

---

## 💡 Pro Tips:

- Use **specific medical terms** for better results
- Ask about **diagnosis**, **treatment**, **workup**, or **management**
- Include **symptom combinations** for differential diagnosis
- Reference **specific diseases** by name

Enjoy searching Harrison's! 🏥

