/**
 * ========================================
 * HABIT TRACKER - Main Application Script
 * ========================================
 */

/**
 * MODAL MANAGEMENT
 */
function openModal() {
  const modal = document.getElementById('modal');
  modal.classList.add('open');
  // Prevent body scroll when modal is open
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  const modal = document.getElementById('modal');
  modal.classList.remove('open');
  // Re-enable body scroll
  document.body.style.overflow = '';
}

// Close modal when clicking on overlay
document.addEventListener('DOMContentLoaded', function () {
  const modalOverlay = document.getElementById('modal');
  if (modalOverlay) {
    modalOverlay.addEventListener('click', function (e) {
      if (e.target === this) {
        closeModal();
      }
    });
  }
});

// Close modal with Escape key
document.addEventListener('keydown', function (e) {
  if (e.key === 'Escape') {
    closeModal();
  }
});

/**
 * COLOR PICKER
 */
document.addEventListener('DOMContentLoaded', function () {
  const colorDots = document.querySelectorAll('.color-dot');
  const selectedColorInput = document.getElementById('selectedColor');

  colorDots.forEach((dot) => {
    dot.addEventListener('click', function () {
      // Remove selected class from all dots
      colorDots.forEach((d) => d.classList.remove('selected'));

      // Add selected class to clicked dot
      this.classList.add('selected');

      // Update hidden input with selected color
      selectedColorInput.value = this.dataset.color;
    });
  });
});

/**
 * CHART MANAGEMENT
 */
const chartCache = {};

async function toggleChart(btn, habitId) {
  const section = document.getElementById('chart-' + habitId);
  const isOpen = section.classList.contains('open');

  section.classList.toggle('open');

  // Update button text
  btn.textContent = section.classList.contains('open') ? '▾ Hide 30-day progress' : '▸ Show 30-day progress';

  // Fetch and render chart only if opening and not already cached
  if (section.classList.contains('open') && !chartCache[habitId]) {
    try {
      const response = await fetch('/api/monthly/' + habitId);
      const data = await response.json();

      chartCache[habitId] = true;

      // Prepare data for chart
      const labels = data.map((d) => d.date.slice(5)); // MM-DD format
      const values = data.map((d) => (d.completed ? 1 : 0)); // 1 or 0

      // Get canvas element
      const canvas = document.getElementById('canvas-' + habitId);
      if (!canvas) return;

      const ctx = canvas.getContext('2d');

      // Create chart instance
      new Chart(ctx, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [
            {
              data: values,
              backgroundColor: values.map((v) => (v ? 'rgba(167, 139, 250, 0.7)' : 'rgba(255, 255, 255, 0.05)')),
              borderRadius: 4,
              borderSkipped: false,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false,
            },
          },
          scales: {
            x: {
              ticks: {
                color: '#6b6b80',
                font: {
                  size: 9,
                },
              },
              grid: {
                display: false,
              },
            },
            y: {
              display: false,
              max: 1.5,
            },
          },
        },
      });
    } catch (error) {
      console.error('Error loading chart data:', error);
    }
  }
}

/**
 * FORM HANDLING
 */
document.addEventListener('DOMContentLoaded', function () {
  // Prevent form submission if needed
  const addHabitForm = document.querySelector('form[action="/add"]');
  if (addHabitForm) {
    addHabitForm.addEventListener('submit', function (e) {
      const name = this.querySelector('input[name="name"]').value.trim();
      if (!name) {
        e.preventDefault();
        alert('Please enter a habit name');
      }
    });
  }
});

/**
 * DELETE CONFIRMATION
 */
function confirmDelete() {
  return confirm('Are you sure you want to delete this habit?');
}

/**
 * UTILITY FUNCTIONS
 */

// Format date to readable format
function formatDate(dateStr) {
  const options = { year: 'numeric', month: 'short', day: 'numeric' };
  return new Date(dateStr).toLocaleDateString('en-US', options);
}

// Log version
console.log('Habit Tracker v1.0 Loaded');
