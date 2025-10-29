const API_BASE = "http://127.0.0.1:5000/api/v1/auth";

async function register() {
  const name = document.getElementById("reg_name").value;
  const email = document.getElementById("reg_email").value;
  const password = document.getElementById("reg_password").value;

  const res = await fetch(`${API_BASE}/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email, password })
  });

  const data = await res.json();
  document.getElementById("output").textContent = JSON.stringify(data, null, 2);
}

async function login() {
  const email = document.getElementById("login_email").value;
  const password = document.getElementById("login_password").value;

  const res = await fetch(`${API_BASE}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ email, password })
  });

  const data = await res.json();
  console.log(data)

  if (res.ok) {
    alert("Đăng nhập thành công!");
  } else {
    alert(data.error || "Sai tài khoản hoặc mật khẩu!");
  }

  document.getElementById("output").textContent = JSON.stringify(data, null, 2);
}
document.getElementById("login-btn").addEventListener("click", login);

async function getAdmin() {
  const token = localStorage.getItem("access_token");
  if (!token) {
    alert("Bạn chưa đăng nhập!");
    return;
  }

  const res = await fetch(`${API_BASE}/admin`, {
    headers: {
      "Authorization": `Bearer ${token}`
    }
  });

  const data = await res.json();
  document.getElementById("output").textContent = JSON.stringify(data, null, 2);
}

async function logout() {
  const res = await fetch(`${API_BASE}/logout`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include"
  })
  
  const data = await res.json();

  console.log(data);

  if (res.ok) {
    alert("Đăng xuất thành công!");
  } else {
    alert(data.error || "Đăng xuất thất bại");
  }
}
