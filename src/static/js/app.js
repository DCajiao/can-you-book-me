'use strict';

const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

document.getElementById('user-tz').textContent = userTimezone;

// ── Modal helpers ────────────────────────────────────────────
const modal      = document.getElementById('event-modal');
const backdrop   = document.getElementById('modal-backdrop');
const closeBtn   = document.getElementById('modal-close');

function openModal(info) {
  const { event } = info;
  const props = event.extendedProps;
  const eventTz = props.event_timezone || 'UTC';

  // Header
  document.getElementById('modal-dot').style.background = event.backgroundColor || '#4f46e5';
  document.getElementById('modal-title').textContent = event.title;

  // Calendar name
  document.getElementById('modal-calendar').textContent = props.calendar_name || '';

  // Time
  const timeRow = document.getElementById('modal-time-row');
  const timeEl  = document.getElementById('modal-time');
  if (event.allDay) {
    timeEl.textContent = formatDate(event.start, userTimezone);
  } else {
    timeEl.textContent = `${formatDateTime(event.start, userTimezone)} – ${formatDateTime(event.end, userTimezone)}`;
  }
  timeRow.classList.remove('hidden');

  // Timezone (only if different from user's)
  const tzRow = document.getElementById('modal-tz-row');
  const tzEl  = document.getElementById('modal-tz');
  if (eventTz && eventTz !== userTimezone) {
    const originalStart = formatDateTime(event.start, eventTz);
    const originalEnd   = event.end ? formatDateTime(event.end, eventTz) : null;
    const originalStr   = originalEnd ? `${originalStart} – ${originalEnd}` : originalStart;
    tzEl.textContent = `Zona original (${eventTz}): ${originalStr}`;
    tzRow.classList.remove('hidden');
  } else {
    tzRow.classList.add('hidden');
  }

  // Location
  const locRow = document.getElementById('modal-location-row');
  const locEl  = document.getElementById('modal-location');
  if (props.location) {
    locEl.textContent = props.location;
    locRow.classList.remove('hidden');
  } else {
    locRow.classList.add('hidden');
  }

  // Description
  const descRow = document.getElementById('modal-desc-row');
  const descEl  = document.getElementById('modal-desc');
  if (props.description) {
    descEl.textContent = props.description;
    descRow.classList.remove('hidden');
  } else {
    descRow.classList.add('hidden');
  }

  modal.classList.remove('hidden');
}

function closeModal() {
  modal.classList.add('hidden');
}

backdrop.addEventListener('click', closeModal);
closeBtn.addEventListener('click', closeModal);
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeModal(); });

// ── Date formatting ──────────────────────────────────────────
function formatDateTime(date, tz) {
  return new Intl.DateTimeFormat('es', {
    timeZone: tz,
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
  }).format(new Date(date));
}

function formatDate(date, tz) {
  return new Intl.DateTimeFormat('es', {
    timeZone: tz,
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(new Date(date));
}

// ── FullCalendar init ────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const calendarEl = document.getElementById('calendar');

  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: 'timeGridWeek',
    locale: 'es',
    timeZone: userTimezone,
    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: 'dayGridMonth,timeGridWeek,timeGridDay',
    },
    height: 'auto',
    nowIndicator: true,
    navLinks: true,
    eventDisplay: 'block',
    slotMinTime: '06:00:00',
    slotMaxTime: '22:00:00',

    events: async (fetchInfo, successCallback, failureCallback) => {
      try {
        const params = new URLSearchParams({
          start: fetchInfo.startStr,
          end:   fetchInfo.endStr,
        });
        const res = await fetch(`/api/events?${params}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        successCallback(data);
      } catch (err) {
        console.error('Error cargando eventos:', err);
        failureCallback(err);
      }
    },

    eventClick: (info) => {
      info.jsEvent.preventDefault();
      openModal(info);
    },

    eventDidMount: (info) => {
      const props = info.event.extendedProps;
      const eventTz = props.event_timezone;

      if (eventTz && eventTz !== userTimezone) {
        // Add a small timezone indicator on the event chip
        const el = info.el.querySelector('.fc-event-title') || info.el;
        if (!el.querySelector('.tz-indicator')) {
          const badge = document.createElement('span');
          badge.className = 'tz-indicator';
          badge.title = `Zona original: ${eventTz}`;
          badge.textContent = ' 🌍';
          badge.style.cssText = 'font-size:0.65rem; opacity:0.8;';
          el.appendChild(badge);
        }
      }
    },
  });

  calendar.render();
});
