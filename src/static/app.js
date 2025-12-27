document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";
      
      // Clear and reset activity select dropdown
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        // Create participants list HTML
        let participantsHTML = '';
        if (details.participants.length > 0) {
          participantsHTML = `
            <div class="participants-section">
              <p class="participants-header"><strong>👥 Participants (${details.participants.length}):</strong></p>
              <ul class="participants-list">
                ${details.participants.map(email => `
                  <li class="participant-item">
                    <span class="participant-email">📧 ${email}</span>
                    <button class="delete-btn" data-activity="${name}" data-email="${email}" title="Unregister participant">
                      ✕
                    </button>
                  </li>
                `).join('')}
              </ul>
            </div>
          `;
        } else {
          participantsHTML = `
            <div class="participants-section">
              <p class="participants-header"><strong>👥 Participants:</strong></p>
              <p class="no-participants">No participants yet. Be the first to sign up!</p>
            </div>
          `;
        }

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          ${participantsHTML}
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        // Refresh the activities list
        fetchActivities();
        
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Handle delete participant
  activitiesList.addEventListener("click", async (event) => {
    if (event.target.classList.contains("delete-btn")) {
      const button = event.target;
      const activity = button.getAttribute("data-activity");
      const email = button.getAttribute("data-email");

      if (!confirm(`Are you sure you want to unregister ${email} from ${activity}?`)) {
        return;
      }

      try {
        const response = await fetch(
          `/activities/${encodeURIComponent(activity)}/unregister?email=${encodeURIComponent(email)}`,
          {
            method: "DELETE",
          }
        );

        const result = await response.json();

        if (response.ok) {
          // Refresh the activities list
          fetchActivities();
          
          // Show success message
          messageDiv.textContent = result.message;
          messageDiv.className = "success";
          messageDiv.classList.remove("hidden");
          
          // Hide message after 5 seconds
          setTimeout(() => {
            messageDiv.classList.add("hidden");
          }, 5000);
        } else {
          messageDiv.textContent = result.detail || "An error occurred";
          messageDiv.className = "error";
          messageDiv.classList.remove("hidden");
        }
      } catch (error) {
        messageDiv.textContent = "Failed to unregister participant. Please try again.";
        messageDiv.className = "error";
        messageDiv.classList.remove("hidden");
        console.error("Error unregistering participant:", error);
      }
    }
  });

  // Initialize app
  fetchActivities();
});
