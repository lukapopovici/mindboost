from fastapi import FastAPI, UploadFile, File
from PyPDF2 import PdfReader
import io
import networkx as nx
from typing import Dict, Any

app = FastAPI()

def extract_knowledge_graph(text: str) -> Dict[str, Any]:
    # Dummy implementation: split text into sentences, create nodes, and link sequentially
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    G = nx.DiGraph()
    for i, sent in enumerate(sentences):
        G.add_node(i, label=sent)
        if i > 0:
            G.add_edge(i-1, i)
    # Format for Recharts: nodes and links
    nodes = [{"id": n, "label": d["label"]} for n, d in G.nodes(data=True)]
    links = [{"source": u, "target": v} for u, v in G.edges()]
    return {"nodes": nodes, "links": links}

@app.post("/knowledge-graph/")
def knowledge_graph(file: UploadFile = File(...)):
    contents = file.file.read()
    reader = PdfReader(io.BytesIO(contents))
    text = " ".join(page.extract_text() or "" for page in reader.pages)
    graph = extract_knowledge_graph(text)
    return graph
