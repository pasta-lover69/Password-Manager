function showErrorModal(message) {
  document.getElementById("error-message").innerText = message;
  document.getElementById("error-modal").style.display = "flex";
}

function closeErrorModal() {
  document.getElementById("error-modal").style.display = "none";
}

function closeModal() {
  document.getElementById("modal").style.display = "none";
}

function showAddPasswordModal() {
  document.getElementById("add-password-modal").style.display = "flex";
}

function showGetPasswordModal() {
  document.getElementById("get-password-modal").style.display = "flex";
}

function closeModal(modalId) {
  document.getElementById(modalId).style.display = "none";
}

function showNotification(message) {
  const notificationModal = document.getElementById("notification-modal");
  const notificationMessage = document.getElementById("notification-message");

  notificationMessage.textContent = message;
  notificationModal.style.display = "block";

  setTimeout(() => {
    notificationModal.style.display = "none";
  }, 3500);
}

async function addPassword() {
  const service = document.getElementById("add-service").value;
  const username = document.getElementById("add-username").value;
  const password = document.getElementById("add-password").value;

  if (!service || !username || !password) {
    showErrorModal("Please fill in all fields.");
    return;
  }

  try {
    const response = await fetch("/add", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ service, username, password })
    });

    const data = await response.json();
    if (response.ok) {
      alert(data.success);
      closeModal("add-password-modal");
    } else {
      showErrorModal(data.error || "An unknown error occurred.");
    }
  } catch (error) {
    showErrorModal("Failed to add password. Please try again.");
    console.error(error);
  }
}

async function getPassword() {
  const service = document.getElementById("get-service").value;
  const username = document.getElementById("get-username").value;

  if (!service || !username) {
    showErrorModal("Please select a service and enter a username.");
    return;
  }

  try {
    const response = await fetch(`/get/${service}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ username })
    });

    const data = await response.json();
    if (response.ok) {
      alert(`Username: ${data.credentials[0].username}\nPassword: ${data.credentials[0].password}`);
      closeModal("get-password-modal");
    } else {
      showErrorModal(data.error || "An unknown error occurred.");
    }
  } catch (error) {
    showErrorModal("Failed to retrieve passwords. Please try again.");
    console.error(error);
  }
}

async function register() {
  const username = document.getElementById("register-username").value.trim();
  const password = document.getElementById("register-password").value.trim();
  const errorElement = document.getElementById("signup-error");

  errorElement.textContent = "";

  if (!username || !password) {
    errorElement.textContent = "Please fill in all fields.";
    return;
  }

  showLoading();
  disableButton("signup-btn");

  try {
    const response = await fetch("/register", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ username, password })
    });

    const data = await response.json();
    if (response.ok) {
      window.location.href = "/profile";
    } else {
      errorElement.textContent = data.error || "An unknown error occurred.";
    }
  } catch (error) {
    errorElement.textContent = "Failed to sign up. Please try again.";
    console.error(error);
  } finally {
    hideLoading();
    enableButton("signup-btn");
  }
}

function showLoading() {
  document.getElementById("loading-spinner").style.display = "block";
}
function hideLoading() {
  document.getElementById("loading-spinner").style.display = "none";
}
function disableButton(btnId) {
  const btn = document.getElementById(btnId);
  if (btn) btn.disabled = true;
}
function enableButton(btnId) {
  const btn = document.getElementById(btnId);
  if (btn) btn.disabled = false;
}

// Example login function
async function login() {
  showLoading();
  disableButton("login-btn");
  // ...your login logic...
  // After login completes (success or error):
  hideLoading();
  enableButton("login-btn");
}

// Example register function
async function register() {
  showLoading();
  disableButton("signup-btn");
  // ...your signup logic...
  // After register completes (success or error):
  hideLoading();
  enableButton("signup-btn");
}

async function login() {
  const username = document.getElementById("login-username").value.trim();
  const password = document.getElementById("login-password").value.trim();
  const errorElement = document.getElementById("login-error");

  errorElement.textContent = "";

  if (!username || !password) {
    errorElement.textContent = "Please fill in all fields.";
    return;
  }

  try {
    const response = await fetch("/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ username, password })
    });

    const data = await response.json();
    if (response.ok) {
      alert("Login successful!");
      window.location.href = "/profile";
    } else {
      errorElement.textContent = data.error || "An unknown error occurred.";
    }
  } catch (error) {
    errorElement.textContent = "Failed to log in. Please try again.";
    console.error(error);
  }
}

async function logout() {
  try {
    const response = await fetch("/logout", {
      method: "POST"
    });

    const data = await response.json();
    if (response.ok) {
      showNotification("Logged out successfully!");
      window.location.href = "/";
    } else {
      alert(data.error || "An unknown error occurred.");
    }
  } catch (error) {
    alert("Failed to log out. Please try again.");
    console.error(error);
  }
}

function exitApp() {
  window.close();
  window.location.href = "about:blank";
}

async function checkSession() {
  try {
    const response = await fetch("/check-session");
    const data = await response.json();

    if (data.logged_in) {
      document.getElementById("auth-section").style.display = "none";
      document.getElementById("password-section").style.display = "block";
    } else {
      document.getElementById("auth-section").style.display = "block";
      document.getElementById("password-section").style.display = "none";
    }
  } catch (error) {
    console.error("Failed to check session:", error);
  }
}

async function populateServiceDropdowns() {
  try {
    const response = await fetch("/get-services", {
      method: "GET",
    });

    if (response.ok) {
      const services = await response.json();
      const addServiceDropdown = document.getElementById("add-service");
      const getServiceDropdown = document.getElementById("get-service");

      addServiceDropdown.innerHTML = '<option value="" disabled selected>Select a service</option>';
      getServiceDropdown.innerHTML = '<option value="" disabled selected>Select a service</option>';

      services.forEach(service => {
        const option = document.createElement("option");
        option.value = service;
        option.textContent = service;

        addServiceDropdown.appendChild(option);
        getServiceDropdown.appendChild(option.cloneNode(true));
      });
    } else {
      console.error("Failed to fetch services.");
    }
  } catch (error) {
    console.error("Error fetching services:", error);
  }
}

async function fetchPasswords() {
  try {
    const response = await fetch("/get-all-passwords", {
      method: "GET",
    });

    if (response.ok) {
      const passwords = await response.json();
      const tableBody = document.getElementById("password-table-body");

      tableBody.innerHTML = "";

      passwords.forEach(({ service, username, password }) => {
        const row = document.createElement("tr");

        const serviceCell = document.createElement("td");
        serviceCell.textContent = service;

        const usernameCell = document.createElement("td");
        usernameCell.textContent = username;

        const passwordCell = document.createElement("td");
        passwordCell.textContent = password;

        row.appendChild(serviceCell);
        row.appendChild(usernameCell);
        row.appendChild(passwordCell);

        tableBody.appendChild(row);
      });
    } else {
      console.error("Failed to fetch passwords.");
    }
  } catch (error) {
    console.error("Error fetching passwords:", error);
  }
}

function togglePasswordVisibility(inputId, toggleButton) {
  const passwordInput = document.getElementById(inputId);
  const isPasswordVisible = passwordInput.type === "text";

  passwordInput.type = isPasswordVisible ? "password" : "text";

  toggleButton.textContent = isPasswordVisible ? "👁️" : "🙈";
}

document.addEventListener("DOMContentLoaded", () => {
  checkSession();
  populateServiceDropdowns();
  fetchPasswords();

  const loginForm = document.getElementById("login-form");
  if (loginForm) {
    loginForm.addEventListener("submit", function (e) {
      e.preventDefault();
      login();
    });
  }

  const signupForm = document.getElementById("signup-form");
  if (signupForm) {
    signupForm.addEventListener("submit", function (e) {
      e.preventDefault();
      register();
    });
  }
});