import React, { useEffect, useState, FormEvent } from "react";
import { motion } from "framer-motion";
import "./App.css";

interface Book {
  id: number;
  title: string;
  author: string;
  available: boolean;
}

interface ApiResponse {
  message?: string;
  error?: string;
}

const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000/api";

export default function App() {
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [user, setUser] = useState("Dat");
  const [newBook, setNewBook] = useState({ title: "", author: "" });
  const [showAdd, setShowAdd] = useState(false);

  useEffect(() => {
    loadBooks();
  }, []);

  async function loadBooks(): Promise<void> {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${BASE_URL}/books`);
      if (!res.ok) throw new Error(`Server returned ${res.status}`);
      const data: Book[] = await res.json();
      setBooks(data);
    } catch (err: any) {
      setError("Cannot connect to server: " + err.message);
    } finally {
      setLoading(false);
    }
  }

  async function borrowBook(book_id: number): Promise<void> {
  try {
    const res = await fetch(`${BASE_URL}/books/${book_id}/borrow`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user }),
    });
    const json: ApiResponse = await res.json();
    if (!res.ok) throw new Error(json.error || json.message || res.statusText);
    alert(json.message);
    await loadBooks();
  } catch (err: any) {
    alert("Borrow failed: " + err.message);
  }
}

async function returnBook(book_id: number): Promise<void> {
  try {
    const res = await fetch(`${BASE_URL}/books/${book_id}/return`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user }),
    });
    const json: ApiResponse = await res.json();
    if (!res.ok) throw new Error(json.error || json.message || res.statusText);
    alert(json.message);
    await loadBooks();
  } catch (err: any) {
    alert("Return failed: " + err.message);
  }
}

  async function addBook(e: FormEvent): Promise<void> {
    e.preventDefault();
    if (!newBook.title.trim() || !newBook.author.trim()) {
      alert("Please provide title and author");
      return;
    }
    try {
      const res = await fetch(`${BASE_URL}/books`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newBook),
      });
      const json: ApiResponse = await res.json();
      if (res.status !== 201) throw new Error(json.error || json.message || res.statusText);
      setNewBook({ title: "", author: "" });
      setShowAdd(false);
      await loadBooks();
    } catch (err: any) {
      alert("Add book failed: " + err.message);
    }
  }

  return (
    <div className="app-container">
      <div className="app-wrapper">
        <header className="app-header">
          <h1>Library</h1>
          <div className="user-input">
            <label>User</label>
            <input
              value={user}
              onChange={(e) => setUser(e.target.value)}
            />
          </div>
        </header>

        <motion.section
          initial={{ opacity: 0, y: -6 }}
          animate={{ opacity: 1, y: 0 }}
          className="app-section"
        >
          <div className="toolbar">
            <div className="buttons">
              <button onClick={loadBooks} className="btn refresh">Refresh</button>
              <button onClick={() => setShowAdd((s) => !s)} className="btn add">Add Book</button>
            </div>
            <div className="api-info">
              API: <code>{BASE_URL}</code>
            </div>
          </div>

          {showAdd && (
            <form onSubmit={addBook} className="add-form">
              <input
                placeholder="Title"
                value={newBook.title}
                onChange={(e) => setNewBook((s) => ({ ...s, title: e.target.value }))}
              />
              <input
                placeholder="Author"
                value={newBook.author}
                onChange={(e) => setNewBook((s) => ({ ...s, author: e.target.value }))}
              />
              <div className="form-actions">
                <button type="submit" className="btn save">Save</button>
                <button type="button" onClick={() => setShowAdd(false)} className="btn cancel">Cancel</button>
              </div>
            </form>
          )}

          {loading ? (
            <div className="loading">Loading...</div>
          ) : error ? (
            <div className="error">{error}</div>
          ) : (
            <table className="book-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Title</th>
                  <th>Author</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {books.map((b) => (
                  <tr key={b.id}>
                    <td>{b.id}</td>
                    <td>{b.title}</td>
                    <td>{b.author}</td>
                    <td>{b.available ? "Available" : "Borrowed"}</td>
                    <td>
                      {b.available ? (
                        <button onClick={() => borrowBook(b.id)} className="btn borrow">Borrow</button>
                      ) : (
                        <button onClick={() => returnBook(b.id)} className="btn return">Return</button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </motion.section>
      </div>
    </div>
  );
}
