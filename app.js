const API_BASE = "https://meatkonnex-backend.onrender.com";

async function fetchAnimals() {
  try {
    const res = await fetch(`${API_BASE}/animals`);
    const animals = await res.json();
    const animalSelect = document.getElementById("animal-select");
    animals.forEach(animal => {
      const option = document.createElement("option");
      option.value = animal.id;
      option.textContent = animal.name;
      animalSelect.appendChild(option);
    });
  } catch (err) {
    alert("Failed to load animals");
    console.error(err);
  }
}

async function fetchMeatParts(animalId) {
  const meatPartSelect = document.getElementById("meat-part-select");
  meatPartSelect.innerHTML = '<option value="">--Select Meat Part--</option>';
  meatPartSelect.disabled = true;

  if (!animalId) return;

  try {
    const res = await fetch(`${API_BASE}/meat_parts/${animalId}`);
    const meatParts = await res.json();
    meatParts.forEach(part => {
      const option = document.createElement("option");
      option.value = part.id;
      option.textContent = part.part_name;
      meatPartSelect.appendChild(option);
    });
    meatPartSelect.disabled = false;
  } catch (err) {
    alert("Failed to load meat parts");
    console.error(err);
  }
}

async function fetchInventory() {
  try {
    const res = await fetch(`${API_BASE}/inventory`);
    const data = await res.json();
    const tbody = document.querySelector("#inventory-table tbody");
    tbody.innerHTML = "";

    data.forEach(item => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${item.inventory_id}</td>
        <td>${item.meat_part}</td>
        <td>${item.animal}</td>
        <td>${item.stock_lb}</td>
        <td>${item.seasoned ? "Yes" : "No"}</td>
        <td>${item.location}</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    alert("Failed to load inventory");
    console.error(err);
  }
}

async function addInventory(event) {
  event.preventDefault();

  const meat_part_id = Number(document.getElementById("meat-part-select").value);
  const current_stock_lb = Number(document.getElementById("stock_lb").value);
  const is_seasoned = document.getElementById("is_seasoned").value === "true";
  const location = document.getElementById("location").value;

  if (!meat_part_id) {
    alert("Please select a meat part.");
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/inventory`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ meat_part_id, current_stock_lb, is_seasoned, location })
    });
    if (!res.ok) throw new Error("Failed to add inventory");

    alert("Inventory added successfully!");
    event.target.reset();
    fetchInventory();
  } catch (err) {
    alert(err.message);
  }
}

document.getElementById("add-inventory-form").addEventListener("submit", addInventory);
document.getElementById("animal-select").addEventListener("change", (e) => {
  fetchMeatParts(e.target.value);
});

fetchAnimals();
fetchInventory();
