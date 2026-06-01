import Documents from "./components/Documents";
import Chat from "./components/Chat";
import "./App.css";

export default function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>RAG Derecho</h1>
      </header>
      <main className="app-body">
        <Documents />
        <Chat />
      </main>
    </div>
  );
}
