'use strict';

/* ── PWA Install ──────────────────────────────────── */
(function initInstall() {
  const btn      = document.getElementById('install-btn');
  const iosTip   = document.getElementById('ios-install-tip');
  const tipClose = document.getElementById('ios-tip-close');

  // Already running as installed PWA — hide everything
  const isStandalone =
    window.matchMedia('(display-mode: standalone)').matches ||
    window.navigator.standalone === true;
  if (isStandalone) return;

  // Only show on mobile screen widths
  const isMobile = () => window.innerWidth < 900;

  // ── Android / Chrome: use beforeinstallprompt ──
  let deferredPrompt = null;

  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    if (isMobile()) btn.classList.remove('hidden');
  });

  btn.addEventListener('click', async () => {
    if (deferredPrompt) {
      // Android / Chrome: native install prompt
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      deferredPrompt = null;
      if (outcome === 'accepted') btn.classList.add('hidden');
    } else {
      // iOS: toggle instruction tooltip
      iosTip.classList.toggle('hidden');
    }
  });

  // ── iOS Safari: detect and show button ──
  const isIOS    = /iphone|ipad|ipod/i.test(navigator.userAgent) && !window.MSStream;
  const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);

  if (isIOS && isSafari && isMobile()) {
    btn.classList.remove('hidden');
  }

  tipClose.addEventListener('click', () => iosTip.classList.add('hidden'));
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') iosTip.classList.add('hidden');
  });
  window.addEventListener('appinstalled', () => btn.classList.add('hidden'));
})();

/* ── Timezone ─────────────────────────────────────── */
const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
document.getElementById('user-tz').textContent = userTimezone;

/* ── Helpers ──────────────────────────────────────── */
function fmtTime(date, tz) {
  return new Intl.DateTimeFormat('es', {
    timeZone: tz,
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  }).format(new Date(date));
}

function fmtDateTime(date, tz) {
  return new Intl.DateTimeFormat('es', {
    timeZone: tz,
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  }).format(new Date(date));
}

function fmtDate(date, tz) {
  return new Intl.DateTimeFormat('es', {
    timeZone: tz,
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(new Date(date));
}

/* ── Modal ────────────────────────────────────────── */
const modal    = document.getElementById('event-modal');
const backdrop = document.getElementById('modal-backdrop');
const closeBtn = document.getElementById('modal-close');

function openModal(info) {
  const { event } = info;
  const p = event.extendedProps;
  const color = event.backgroundColor || '#c9a14a';
  const eventTz = p.event_timezone || userTimezone;

  document.getElementById('modal-color-bar').style.background = color;
  document.getElementById('modal-calendar').textContent = p.calendar_name || '';
  document.getElementById('modal-title').textContent = event.title;

  // Use startStr/endStr (ISO with offset) so new Date() resolves the real UTC
  // moment before Intl converts to the target timezone — avoids double-offset.
  const startDate = new Date(event.startStr);
  const endDate   = event.endStr ? new Date(event.endStr) : null;

  // Time
  const timeEl = document.getElementById('modal-time');
  if (event.allDay) {
    timeEl.textContent = fmtDate(startDate, userTimezone);
  } else {
    const s = fmtDateTime(startDate, userTimezone);
    const e = endDate ? fmtTime(endDate, userTimezone) : '';
    timeEl.textContent = e ? `${s} → ${e}` : s;
  }

  // Original timezone
  const tzRow = document.getElementById('detail-tz');
  const tzEl  = document.getElementById('modal-tz');
  if (eventTz && eventTz !== userTimezone && !p.is_busy) {
    const s = fmtDateTime(startDate, eventTz);
    const e = endDate ? fmtTime(endDate, eventTz) : '';
    tzEl.textContent = `${eventTz}: ${s}${e ? ' → ' + e : ''}`;
    tzRow.classList.remove('hidden');
  } else {
    tzRow.classList.add('hidden');
  }

  // Location
  const locRow = document.getElementById('detail-location');
  const locEl  = document.getElementById('modal-location');
  if (p.location && !p.is_busy) {
    locEl.textContent = p.location;
    locRow.classList.remove('hidden');
  } else {
    locRow.classList.add('hidden');
  }

  // Description
  const descRow = document.getElementById('detail-desc');
  const descEl  = document.getElementById('modal-desc');
  if (p.description && !p.is_busy) {
    descEl.textContent = p.description;
    descRow.classList.remove('hidden');
  } else {
    descRow.classList.add('hidden');
  }

  modal.classList.remove('hidden');
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  modal.classList.add('hidden');
  document.body.style.overflow = '';
}

backdrop.addEventListener('click', closeModal);
closeBtn.addEventListener('click', closeModal);
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });

// Swipe-down to close on mobile
let touchStartY = 0;
modal.addEventListener('touchstart', e => { touchStartY = e.touches[0].clientY; }, { passive: true });
modal.addEventListener('touchend', e => {
  if (e.changedTouches[0].clientY - touchStartY > 80) closeModal();
}, { passive: true });

/* ── Custom event chip renderer ──────────────────── */
function renderEventContent(arg) {
  const event = arg.event;
  const p = event.extendedProps;
  const color = event.backgroundColor || '#c9a14a';
  const isBusy = p.is_busy;
  const hasOtherTz = p.event_timezone && p.event_timezone !== userTimezone;
  const isTimeGrid = arg.view.type.includes('timeGrid');

  const chip = document.createElement('div');
  chip.className = 'cal-chip';
  chip.style.setProperty('--chip-color', color);

  // Title
  const titleEl = document.createElement('span');
  titleEl.className = 'chip-title' + (isBusy ? ' busy' : '');
  titleEl.textContent = event.title;
  chip.appendChild(titleEl);

  // Time row (only in time grid and if not all-day)
  if (isTimeGrid && !event.allDay && event.startStr) {
    const timeEl = document.createElement('span');
    timeEl.className = 'chip-time';
    const s = fmtTime(new Date(event.startStr), userTimezone);
    const e = event.endStr ? fmtTime(new Date(event.endStr), userTimezone) : '';
    timeEl.textContent = e ? `${s}–${e}` : s;
    chip.appendChild(timeEl);
  }

  // Timezone indicator
  if (hasOtherTz && !isBusy) {
    const tzEl = document.createElement('span');
    tzEl.className = 'chip-tz';
    tzEl.title = `Zona original: ${p.event_timezone}`;
    tzEl.textContent = '🌍';
    chip.appendChild(tzEl);
  }

  return { domNodes: [chip] };
}

/* ── Responsive initial view ─────────────────────── */
function getInitialView() {
  const w = window.innerWidth;
  if (w < 480) return 'listWeek';
  if (w < 768) return 'timeGridDay';
  return 'timeGridWeek';
}


/* ── FullCalendar ─────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  const calEl = document.getElementById('calendar');

  const calendar = new FullCalendar.Calendar(calEl, {
    initialView: getInitialView(),
    locale: 'es',
    timeZone: userTimezone,

    headerToolbar: {
      left:   'prev,next today',
      center: 'title',
      right:  'timeGridDay,timeGridWeek,dayGridMonth,listWeek',
    },

    buttonText: {
      today:    'Hoy',
      day:      'Día',
      week:     'Semana',
      month:    'Mes',
      list:     'Lista',
    },

    height: 'auto',
    nowIndicator: true,
    navLinks: true,
    slotMinTime: '07:00:00',
    slotMaxTime: '23:00:00',
    allDaySlot: true,
    slotDuration: '00:15:00',
    slotLabelInterval: '01:00',
    eventContent: renderEventContent,

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

    loading: (isLoading) => {
      const overlay = document.getElementById('loading-overlay');
      if (isLoading) {
        overlay.classList.remove('hidden');
      } else {
        overlay.classList.add('hidden');
      }
    },

    eventClick: (info) => {
      info.jsEvent.preventDefault();
      openModal(info);
    },

    // Responsive: switch view on resize
    windowResize: (arg) => {
      const view = getInitialView();
      if (arg.view.type !== view) {
        arg.view.calendar.changeView(view);
      }
    },
  });

  // Show loader before first render so it's visible from the start
  document.getElementById('loading-overlay').classList.remove('hidden');
  calendar.render();
});
