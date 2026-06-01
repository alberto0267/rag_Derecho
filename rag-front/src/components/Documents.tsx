import { useRef } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getDocuments, uploadDocument, deleteDocument } from "../api";

interface Document {
  filename: string;
  chunks: number;
}

export default function Documents() {
  const queryClient = useQueryClient();
  const inputRef = useRef<HTMLInputElement>(null);

  const { data: docs = [] } = useQuery<Document[]>({
    queryKey: ["documents"],
    queryFn: getDocuments,
  });

  const uploadMutation = useMutation({
    mutationFn: (file: File) => uploadDocument(file),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["documents"] }),
  });

  const deleteMutation = useMutation({
    mutationFn: (filename: string) => deleteDocument(filename),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["documents"] }),
  });

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    await uploadMutation.mutateAsync(file);
    if (inputRef.current) inputRef.current.value = "";
  }

  return (
    <aside className="documents-panel">
      <h2>Documentos</h2>

      <button
        className="upload-btn"
        onClick={() => inputRef.current?.click()}
        disabled={uploadMutation.isPending}
      >
        {uploadMutation.isPending ? "Subiendo..." : "+ Subir PDF"}
      </button>
      <input ref={inputRef} type="file" accept=".pdf,.docx" onChange={handleUpload} hidden />

      <ul className="doc-list">
        {docs.length === 0 && <li className="empty">Sin documentos</li>}
        {docs.map((doc) => (
          <li key={doc.filename} className="doc-item">
            <span className="doc-name" title={doc.filename}>📄 {doc.filename}</span>
            <span className="doc-chunks">{doc.chunks} chunks</span>
            <button
              className="delete-btn"
              onClick={() => deleteMutation.mutate(doc.filename)}
              disabled={deleteMutation.isPending}
            >
              ✕
            </button>
          </li>
        ))}
      </ul>
    </aside>
  );
}
