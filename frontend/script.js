const API_URL = "http://127.0.0.1:5000";

// ---- Section Switching ----
function showSection(sectionId) {
  document.querySelectorAll(".section").forEach(sec => sec.classList.add("hidden"));
  document.querySelector(`#${sectionId}`).classList.remove("hidden");

  document.querySelectorAll(".tabs button").forEach(btn => btn.classList.remove("active"));
  document.querySelector(`.tabs button[onclick="showSection('${sectionId}')"]`).classList.add("active");

  // Auto-load accounts when switching to accounts tab
  if (sectionId === "accounts") fetchAccounts();
}

// ---- Create Account ----
document.getElementById("createAccountForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const ownerName = document.getElementById("ownerName").value;
  const initialDeposit = parseFloat(document.getElementById("initialDeposit").value);

  const res = await fetch(`${API_URL}/accounts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ owner_name: ownerName, initial_deposit: initialDeposit })
  });

  if (res.ok) {
    alert("✅ Account created!");
    e.target.reset();
  } else {
    alert("❌ Error creating account");
  }
});

// ---- Transfer Money ----
document.getElementById("transferForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fromAccount = parseInt(document.getElementById("fromAccount").value);
  const toAccount = parseInt(document.getElementById("toAccount").value);
  const amount = parseFloat(document.getElementById("amount").value);

  const res = await fetch(`${API_URL}/transfer`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ from_account_id: fromAccount, to_account_id: toAccount, amount })
  });

  if (res.ok) {
    alert("✅ Transfer successful!");
    e.target.reset();
  } else {
    const error = await res.json();
    alert(`❌ Error: ${error.detail}`);
  }
});

// ---- Fetch Accounts ----
async function fetchAccounts() {
  const res = await fetch(`${API_URL}/accounts`);
  const data = await res.json();
  const tbody = document.querySelector("#accountsTable tbody");
  tbody.innerHTML = "";

  data.forEach(acc => {
    const row = `<tr>
      <td>${acc.id}</td>
      <td>${acc.owner_name}</td>
      <td>💲 ${acc.balance.toFixed(2)}</td>
    </tr>`;
    tbody.innerHTML += row;
  });
}

// Default view
window.onload = () => showSection("create");
