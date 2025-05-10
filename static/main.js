async function addPassword() {
  const service = document.getElementById("service").value;
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  if (!service) {
    document.getElementById("result").innerText = "Error: Please select a service.";
    return;
  }

  const response = await fetch("/add", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ service, username, password })
  });

  const data = await response.json();
  document.getElementById("result").innerText = data.success
    ? "Password added successfully!"
    : "Error: " + data.error;
}

async function getPassword() {
  const service = document.getElementById("service").value;

  if (!service) {
    document.getElementById("result").innerText = "Error: Please select a service.";
    return;
  }

  const response = await fetch(`/get/${service}`);
  if (!response.ok) {
    document.getElementById("result").innerText = "Error: " + response.statusText;
    return;
  }

  const data = await response.json();

  if (data.username) {
    document.getElementById("modal-service").innerText = `Service: ${service}`;
    document.getElementById("modal-username").innerText = data.username;
    document.getElementById("modal-password").innerText = data.password;

    document.getElementById("modal").style.display = "flex";
  } else {
    document.getElementById("result").innerText = "Error: " + data.error;
  }
}

function closeModal() {
  document.getElementById("modal").style.display = "none";
}

function exitApp() {
  window.close();
  window.location.href = "about:blank";
}