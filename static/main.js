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
  document.getElementById("get-password-modal").style.display = "block";
  populateServiceDropdowns();
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
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ service, username, password }),
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
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username }),
    });

    const data = await response.json();
    if (response.ok) {
      alert(
        `Username: ${data.credentials[0].username}\nPassword: ${data.credentials[0].password}`
      );
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
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username, password }),
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

async function signup() {
  const username = document.getElementById("signup-username").value.trim();
  const password = document.getElementById("signup-password").value.trim();
  const confirmPassword = document
    .getElementById("signup-confirm-password")
    .value.trim();
  const errorElement = document.getElementById("signup-error");

  // Clear previous errors
  errorElement.textContent = "";

  // Validation
  if (!username || !password || !confirmPassword) {
    errorElement.textContent = "Please fill in all fields.";
    return;
  }

  if (password !== confirmPassword) {
    errorElement.textContent = "Passwords do not match.";
    return;
  }

  if (password.length < 6) {
    errorElement.textContent = "Password must be at least 6 characters long.";
    return;
  }

  try {
    console.log("Attempting signup for:", username); // Debug log

    const response = await fetch("/register", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username, password }),
    });

    console.log("Signup response status:", response.status); // Debug log
    const data = await response.json();
    console.log("Signup response data:", data); // Debug log

    if (response.ok) {
      alert("Registration successful! Redirecting to your profile...");
      // Redirect to profile page
      window.location.href = "/profile";
    } else {
      errorElement.textContent = data.error || "Registration failed.";
    }
  } catch (error) {
    console.error("Signup error:", error);
    errorElement.textContent = "Registration failed. Please try again.";
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
    console.log("Attempting login for:", username); // Debug log

    const response = await fetch("/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username, password }),
    });

    console.log("Login response status:", response.status); // Debug log
    const data = await response.json();
    console.log("Login response data:", data); // Debug log

    if (response.ok) {
      console.log("Login successful, redirecting..."); // Debug log
      alert("Login successful!");
      window.location.href = "/profile";
    } else {
      errorElement.textContent = data.error || "Login failed.";
    }
  } catch (error) {
    console.error("Login error:", error);
    errorElement.textContent = "Failed to log in. Please try again.";
  }
}

async function logout() {
  try {
    const response = await fetch("/logout", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    const data = await response.json();
    if (response.ok) {
      alert("Logged out successfully!");
      // Redirect to login page
      window.location.href = "/";
    } else {
      alert("Error logging out: " + (data.error || "Unknown error"));
    }
  } catch (error) {
    console.error("Logout error:", error);
    alert("Failed to log out. Please try again.");
  }
}

async function checkAuthStatus() {
  try {
    const response = await fetch("/check-session");
    const data = await response.json();

    const logoutBtn = document.getElementById("logout-btn");
    const loginSection = document.getElementById("login-section");

    if (data.logged_in) {
      if (logoutBtn) logoutBtn.style.display = "block";
      if (loginSection) loginSection.style.display = "none";
    } else {
      if (logoutBtn) logoutBtn.style.display = "none";
      if (loginSection) loginSection.style.display = "block";
    }
  } catch (error) {
    console.error("Auth check error:", error);
  }
}

// Added this function to check if user is properly logged in
async function checkAuthenticationStatus() {
  try {
    const response = await fetch("/check-session");
    const data = await response.json();

    console.log("Auth status:", data); // Debug log

    if (!data.logged_in) {
      // User is not logged in, redirect to home
      window.location.href = "/";
    }

    return data.logged_in;
  } catch (error) {
    console.error("Auth check error:", error);
    return false;
  }
}

// Call this when profile page loads
if (window.location.pathname === "/profile") {
  document.addEventListener("DOMContentLoaded", checkAuthenticationStatus);
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

function populateServiceDropdowns() {
  fetch("/get-services")
    .then((res) => res.json())
    .then((services) => {
      const getServiceSelect = document.getElementById("get-service");
      if (getServiceSelect) {
        getServiceSelect.innerHTML = "";
        services.forEach((service) => {
          const option = document.createElement("option");
          option.value = service;
          option.textContent = service;
          getServiceSelect.appendChild(option);
        });
      }
    });
}

// Modal control functions
function openGetPasswordModal() {
  const modal = document.getElementById("getPasswordModal");
  modal.style.display = "block";

  // Load available services
  loadUserServices();

  // Reset form
  document.getElementById("getService").value = "";
  document.getElementById("getUsername").value = "";
  document.getElementById("passwordResult").style.display = "none";
}

function closeGetPasswordModal() {
  const modal = document.getElementById("getPasswordModal");
  modal.style.display = "none";
}

// Close modal when clicking outside
window.onclick = function (event) {
  const modal = document.getElementById("getPasswordModal");
  if (event.target == modal) {
    closeGetPasswordModal();
  }
};

// Load user's services into dropdown
async function loadUserServices() {
  try {
    const response = await fetch("/get-services");
    const services = await response.json();

    const serviceSelect = document.getElementById("getService");

    // Clear existing options except the first one
    while (serviceSelect.children.length > 1) {
      serviceSelect.removeChild(serviceSelect.lastChild);
    }

    // Add user's services
    services.forEach((service) => {
      const option = document.createElement("option");
      option.value = service;
      option.textContent = service;
      serviceSelect.appendChild(option);
    });

    // Add common services that might not be in user's list
    const commonServices = [
      "Facebook",
      "Twitter",
      "Instagram",
      "Netflix",
      "Spotify",
      "TikTok",
      "Other",
    ];
    commonServices.forEach((service) => {
      // Check if service already exists
      let exists = false;
      for (let i = 1; i < serviceSelect.children.length; i++) {
        if (serviceSelect.children[i].value === service) {
          exists = true;
          break;
        }
      }

      if (!exists) {
        const option = document.createElement("option");
        option.value = service;
        option.textContent = service;
        serviceSelect.appendChild(option);
      }
    });
  } catch (error) {
    console.error("Error loading services:", error);
  }
}

// Retrieve password function
async function retrievePassword() {
  const service = document.getElementById("getService").value.trim();
  const username = document.getElementById("getUsername").value.trim();
  const resultDiv = document.getElementById("passwordResult");
  const passwordDisplay = document.getElementById("retrievedPassword");

  // Validation
  if (!service) {
    alert("Please select a service.");
    return;
  }

  if (!username) {
    alert("Please enter a username/email.");
    return;
  }

  try {
    const response = await fetch(`/get/${encodeURIComponent(service)}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username: username }),
    });

    const data = await response.json();

    if (response.ok) {
      // Display the password
      passwordDisplay.textContent = data.password;
      resultDiv.style.display = "block";

      // Show success message
      showNotification("Password retrieved successfully!", "success");
    } else {
      // Show error message
      alert("Error: " + (data.error || "Password not found"));
      resultDiv.style.display = "none";
    }
  } catch (error) {
    console.error("Error retrieving password:", error);
    alert("Failed to retrieve password. Please try again.");
    resultDiv.style.display = "none";
  }
}

// Copy password to clipboard
async function copyPassword() {
  const passwordText = document.getElementById("retrievedPassword").textContent;

  try {
    await navigator.clipboard.writeText(passwordText);
    showNotification("Password copied to clipboard!", "success");
  } catch (error) {
    // Fallback for older browsers
    const textArea = document.createElement("textarea");
    textArea.value = passwordText;
    document.body.appendChild(textArea);
    textArea.select();
    document.execCommand("copy");
    document.body.removeChild(textArea);
    showNotification("Password copied to clipboard!", "success");
  }
}

// Notification function
function showNotification(message, type = "info") {
  // Create notification element
  const notification = document.createElement("div");
  notification.className = `notification ${type}`;
  notification.textContent = message;

  // Style the notification
  notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 5px;
        color: white;
        font-weight: bold;
        z-index: 10000;
        opacity: 0;
        transition: opacity 0.3s;
        ${
          type === "success"
            ? "background-color: #28a745;"
            : "background-color: #007bff;"
        }
    `;

  // Add to page
  document.body.appendChild(notification);

  // Show notification
  setTimeout(() => (notification.style.opacity = "1"), 100);

  // Remove notification after 3 seconds
  setTimeout(() => {
    notification.style.opacity = "0";
    setTimeout(() => document.body.removeChild(notification), 300);
  }, 3000);
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

  checkAuthStatus();
});
