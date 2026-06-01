const BASE_URL = "http://localhost:8000";

export async function getDocuments() {
  const res = await fetch(`${BASE_URL}/documents`);
  return res.json();
}

export async function uploadDocument(file: File) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE_URL}/upload`, { method: "POST", body: form });
  return res.json();
}

export async function deleteDocument(filename: string) {
  const res = await fetch(`${BASE_URL}/documents/${encodeURIComponent(filename)}`, {
    method: "DELETE",
  });
  return res.json();
}

export async function query(question: string, history: { role: string; content: string }[]) {
  const res = await fetch(`${BASE_URL}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, history }),
  });
  return res.json();
}
