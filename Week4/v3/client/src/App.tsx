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
  token?: string;
}

const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000/api/v3";

export default function App() {
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [user, setUser] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState<string | null>(localStorage.getItem("token"));
  const [newBook, setNewBook] = useState({ title: "", author: "" });
  const [showAdd, setShowAdd] = useState(false);

  useEffect(() => {
    if (token) loadBooks();
  }, [token]);

  async function login(e: FormEvent): Promise<void> {
    e.preventDefault();
    if (!user.trim()) {
      alert("Enter username");
      return;
    }
    try {
      const res = await fetch(`${BASE_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: user, password }),
      });
      const json: ApiResponse = await res.json();
      if (!res.ok || !json.token) throw new Error(json.error || "Login failed");
      localStorage.setItem("token", json.token);
      setToken(json.token);
    } catch (err: any) {
      alert("Login failed: " + err.message);
    }
  }

  async function loadBooks(): Promise<void> {
    if (!token) return;
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${BASE_URL}/books/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
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
    if (!token) return;
    try {
      const res = await fetch(`${BASE_URL}/books/${book_id}/borrow/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
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
    if (!token) return;
    try {
      const res = await fetch(`${BASE_URL}/books/${book_id}/return/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });
      const json: ApiResponse = await res.json();
      if (!res.ok) throw new Error(json.error || json.message || res.statusText);
      alert(json.message);
      await loadBooks();
    } catch (err: any) {
      alert("Return failed: " + err.message);
    }
  }

  function logout() {
    localStorage.removeItem("token");
    setToken(null);
    setBooks([]);
  }

  if (!token) {
    return (
      <div className="login-container">
        <h2>Library Login</h2>
        <form onSubmit={login}>
          <input
            placeholder="Enter username"
            value={user}
            onChange={(e) => setUser(e.target.value)}
          />
          <input
  type="password"
  placeholder="Enter password"
  value={password}
  onChange={(e) => setPassword(e.target.value)}
/>
          <button type="submit" className="btn login">Login</button>
        </form>
      </div>
    );
  }

  return (
    <div className="app-container">
      <div className="app-wrapper">
        <header className="app-header">
          <h1>Library (v3 Stateless)</h1>
          <div className="user-info">
            <span>Logged in as <b>{user || "User"}</b></span>
            <button onClick={logout} className="btn logout">Logout</button>
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
            <form onSubmit={(e) => e.preventDefault()} className="add-form">
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
