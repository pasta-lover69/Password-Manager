// Function to show the error modal
function showErrorModal(message) {
  document.getElementById("error-message").innerText = message;
  document.getElementById("error-modal").style.display = "flex";
}

// Function to close the error modal
function closeErrorModal() {
  document.getElementById("error-modal").style.display = "none";
}

// Function to close the main modal
function closeModal() {
  document.getElementById("modal").style.display = "none";
}

// Update existing functions to use the error modal
async function addPassword() {
  const service = document.getElementById("service").value;
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  if (!service || !username || !password) {
    showErrorModal("Please fill in all fields.");
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
  if (!data.success) {
    showErrorModal(data.error || "An unknown error occurred.");
  } else {
    document.getElementById("result").innerText = "Password added successfully!";
  }
}

async function getPassword() {
  const service = document.getElementById("service").value;

  if (!service) {
    showErrorModal("Please select a service.");
    return;
  }

  try {
    const response = await fetch(`/get/${service}`);
    if (!response.ok) {
      showErrorModal("Error: " + response.statusText);
      return;
    }

    const data = await response.json();

    if (data.username) {
      // Set the service logo
      const logoMap = {
        Facebook: "https://upload.wikimedia.org/wikipedia/commons/5/51/Facebook_f_logo_%282019%29.svg",
        Spotify: "https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg",
        Netflix: "https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg",
        Instagram: "https://upload.wikimedia.org/wikipedia/commons/a/a5/Instagram_icon.png",
        Twitter: "https://upload.wikimedia.org/wikipedia/commons/6/60/Twitter_Logo_as_of_2021.svg",
        TikTok: "https://upload.wikimedia.org/wikipedia/en/6/69/TikTok_logo.svg",
      };

      const logoUrl = logoMap[service] || "https://via.placeholder.com/50"; // Default logo if service not found
      document.getElementById("modal-logo").src = logoUrl;

      // Populate modal with service details
      document.getElementById("modal-service").innerText = `Service: ${service}`;
      document.getElementById("modal-username").innerText = data.username;
      document.getElementById("modal-password").innerText = data.password;

      // Show the modal
      document.getElementById("modal").style.display = "flex";
    } else {
      showErrorModal(data.error || "Service not found.");
    }
  } catch (error) {
    showErrorModal("An error occurred while retrieving the data.");
    console.error(error);
  }
}

function exitApp() {
  window.close();
  window.location.href = "about:blank";
}