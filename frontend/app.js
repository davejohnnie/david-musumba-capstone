const API_URL = "/api";

const form = document.getElementById("claim-form");
const memberInput = document.getElementById("member-name");
const facilityInput = document.getElementById("facility");
const amountInput = document.getElementById("amount");
const tableBody = document.getElementById("claims-table");

async function loadClaims() {
  const res = await fetch(`${API_URL}/claims`);
  const claims = await res.json();
  tableBody.innerHTML = "";
  claims.forEach(renderClaim);
}

function renderClaim(claim) {
  const row = document.createElement("tr");

  row.innerHTML = `
    <td>${claim.member_name}</td>
    <td>${claim.facility}</td>
    <td>${claim.amount}</td>
    <td><span class="badge badge-${claim.status}">${claim.status}</span></td>
    <td></td>
  `;

  const actionsCell = row.querySelector("td:last-child");

  const approveBtn = document.createElement("button");
  approveBtn.className = "btn btn-sm btn-outline-success me-1";
  approveBtn.textContent = "Approve";
  approveBtn.onclick = () => updateStatus(claim.id, "approved");

  const rejectBtn = document.createElement("button");
  rejectBtn.className = "btn btn-sm btn-outline-danger me-1";
  rejectBtn.textContent = "Reject";
  rejectBtn.onclick = () => updateStatus(claim.id, "rejected");

  const deleteBtn = document.createElement("button");
  deleteBtn.className = "btn btn-sm btn-outline-secondary";
  deleteBtn.textContent = "Delete";
  deleteBtn.onclick = () => deleteClaim(claim.id);

  actionsCell.appendChild(approveBtn);
  actionsCell.appendChild(rejectBtn);
  actionsCell.appendChild(deleteBtn);
  tableBody.appendChild(row);
}

async function updateStatus(id, status) {
  await fetch(`${API_URL}/claims/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status })
  });
  loadClaims();
}

async function deleteClaim(id) {
  await fetch(`${API_URL}/claims/${id}`, { method: "DELETE" });
  loadClaims();
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  await fetch(`${API_URL}/claims`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      member_name: memberInput.value,
      facility: facilityInput.value,
      amount: parseFloat(amountInput.value)
    })
  });
  form.reset();
  loadClaims();
});

loadClaims();