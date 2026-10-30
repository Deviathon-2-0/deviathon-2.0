/**
 * IMAIRA+ Unified User Session & Top-Right Profile Manager
 * frontend/js/user-session.js
 *
 * Provides:
 * 1. Default mock users registry (Ravi Kisan, Priya Sharma, Arjun Mehta).
 * 2. Dynamic top-right profile pill and interactive modal/dropdown.
 * 3. One-click account switcher with persistent localStorage syncing.
 * 4. Cross-page live synchronization with custom and storage events.
 */

const IMAIRA_MOCK_USERS = [
  {
    id: "ravi-kisan",
    name: "Ravi Kisan",
    email: "ravi.kisan@gmail.com",
    password: "Ravi@Google2026",
    role: "Senior Distributed Systems Architect",
    company: "Google",
    targetTrack: "Distributed Systems & High-Throughput APIs",
    bio: "Principal backend & systems architect specializing in Raft consensus, zero-loss Kafka streaming, and sub-10ms gRPC microservices.",
    avatar: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=256&q=80",
    initials: "RK",
    score: 89.5,
    benchmarkSessionId: "11111111-2222-3333-4444-555555555551"
  },
  {
    id: "priya-sharma",
    name: "Priya Sharma",
    email: "priya.sharma@meta.com",
    password: "Priya@Meta2026",
    role: "Staff Full Stack & Product Lead",
    company: "Meta",
    targetTrack: "End-to-End Modern Web Architecture & Micro-Frontends",
    bio: "Product-minded staff engineer scaling React core, WebAssembly interactive rendering, and GraphQL federation layers.",
    avatar: "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=256&q=80",
    initials: "PS",
    score: 88.0,
    benchmarkSessionId: "11111111-2222-3333-4444-555555555551"
  },
  {
    id: "arjun-mehta",
    name: "Arjun Mehta",
    email: "arjun.mehta@aws.com",
    password: "Arjun@Amazon2026",
    role: "Principal Cloud Infrastructure Lead",
    company: "Amazon",
    targetTrack: "Multi-Region Cloud Topologies & Kubernetes Reliability",
    bio: "Cloud infrastructure architect optimizing multi-region AWS topologies, chaos engineering, and zero-trust service meshes.",
    avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=256&q=80",
    initials: "AM",
    score: 87.5,
    benchmarkSessionId: "11111111-2222-3333-4444-555555555551"
  }
];

class UserSessionManager {
  constructor() {
    this.storageKey = 'imaira_profile';
    this.mockUsers = IMAIRA_MOCK_USERS;
    this.init();
  }

  init() {
    // If no user set, default to Ravi Kisan
    if (!localStorage.getItem(this.storageKey)) {
      this.setActiveUserById('ravi-kisan');
    }

    // Listen to storage events across tabs
    window.addEventListener('storage', (e) => {
      if (e.key === this.storageKey) {
        this.syncUI();
      }
    });

    // Listen to local in-page profile update events
    window.addEventListener('imaira:profile-updated', () => {
      this.syncUI();
    });

    // Inject top-right profile component once DOM is ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.mountTopRightProfile());
    } else {
      this.mountTopRightProfile();
    }
  }

  getActiveUser() {
    try {
      const data = localStorage.getItem(this.storageKey);
      if (data) {
        return JSON.parse(data);
      }
    } catch (e) {}
    return this.mockUsers[0];
  }

  setActiveUserById(userId) {
    const user = this.mockUsers.find(u => u.id === userId) || this.mockUsers[0];
    localStorage.setItem(this.storageKey, JSON.stringify(user));
    window.dispatchEvent(new CustomEvent('imaira:profile-updated', { detail: user }));
    this.syncUI();
    return user;
  }

  updateProfile(updates) {
    const current = this.getActiveUser();
    const updated = { ...current, ...updates };
    
    // Auto calculate initials if name changed
    if (updates.name) {
      const parts = updates.name.trim().split(/\s+/);
      updated.initials = (parts[0][0] + (parts[1] ? parts[1][0] : '')).toUpperCase();
    }

    localStorage.setItem(this.storageKey, JSON.stringify(updated));
    window.dispatchEvent(new CustomEvent('imaira:profile-updated', { detail: updated }));
    this.syncUI();
    return updated;
  }

  mountTopRightProfile() {
    // Find or create top-right header container
    const existing = document.getElementById('imaira-top-right-profile');
    if (existing) return;

    // Check if target container exists, otherwise look for header or prepend to main
    let target = document.getElementById('workspace-header-actions');
    if (!target) {
      const header = document.querySelector('header');
      if (header) {
        target = header;
      }
    }

    const user = this.getActiveUser();

    // Create Profile Widget DOM
    const widget = document.createElement('div');
    widget.id = 'imaira-top-right-profile';
    widget.className = 'relative inline-block text-left z-50';
    widget.innerHTML = `
      <!-- Trigger Button -->
      <button id="imaira-profile-trigger" type="button" class="flex items-center gap-2.5 p-1.5 sm:px-3 sm:py-1.5 rounded-full bg-white border border-[#E8DFD0] hover:border-[#AA7000] hover:shadow-sm transition-all shadow-xs cursor-pointer group">
        <div class="w-8 h-8 rounded-full overflow-hidden bg-[#2C1F0E] text-white font-bold flex items-center justify-center text-xs shrink-0 border border-[#E8DFD0] relative">
          <img id="imaira-badge-avatar" src="${user.avatar}" alt="${user.name}" class="w-full h-full object-cover ${user.avatar ? '' : 'hidden'}" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';" />
          <span id="imaira-badge-initials" class="${user.avatar ? 'hidden' : 'flex'} items-center justify-center w-full h-full">${user.initials || 'RK'}</span>
          <span class="absolute bottom-0 right-0 w-2 h-2 rounded-full bg-emerald-500 border border-white"></span>
        </div>
        <div class="hidden sm:block text-left pr-1">
          <div id="imaira-badge-name" class="text-xs font-bold text-[#2C1F0E] leading-tight group-hover:text-[#AA7000] transition-colors">${user.name}</div>
          <div id="imaira-badge-company" class="text-[10px] text-[#7F766C] font-semibold">${user.company || 'Google'} Target</div>
        </div>
        <span class="material-symbols-outlined text-sm text-[#7F766C] group-hover:text-[#2C1F0E] transition-transform" id="imaira-badge-caret">expand_more</span>
      </button>

      <!-- Floating Dropdown Modal -->
      <div id="imaira-profile-dropdown" class="hidden absolute right-0 mt-2 w-80 sm:w-96 rounded-2xl bg-white border border-[#E8DFD0] shadow-2xl p-4 z-50 transition-all transform origin-top-right">
        <!-- User Bio Card -->
        <div class="flex items-start gap-3 pb-3 border-b border-[#E8DFD0]">
          <div class="w-12 h-12 rounded-full overflow-hidden bg-[#2C1F0E] text-white font-bold flex items-center justify-center text-sm shrink-0 border border-[#E8DFD0]">
            <img id="imaira-modal-avatar" src="${user.avatar}" alt="${user.name}" class="w-full h-full object-cover ${user.avatar ? '' : 'hidden'}" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';" />
            <span id="imaira-modal-initials" class="${user.avatar ? 'hidden' : 'flex'} items-center justify-center w-full h-full">${user.initials || 'RK'}</span>
          </div>
          <div class="min-w-0 flex-1">
            <div class="flex items-center justify-between">
              <h3 id="imaira-modal-name" class="text-sm font-extrabold text-[#2C1F0E] truncate">${user.name}</h3>
              <span id="imaira-modal-score" class="px-2 py-0.5 rounded-full bg-[#FAF3E0] text-[#AA7000] text-[10px] font-black border border-[#AA7000]/20">${user.score || 89.5} Pts</span>
            </div>
            <p id="imaira-modal-role" class="text-xs text-[#7F766C] font-medium truncate">${user.role}</p>
            <p id="imaira-modal-email" class="text-[11px] text-[#8C7B6B] truncate">${user.email}</p>
          </div>
        </div>

        <!-- Google Benchmark Report Banner -->
        <a href="report.html?sessionId=${user.benchmarkSessionId || '11111111-2222-3333-4444-555555555551'}" class="mt-3 p-3 rounded-xl bg-gradient-to-r from-[#FAF3E0] via-white to-[#FAF3E0] border border-[#AA7000]/30 hover:border-[#AA7000] transition-all flex items-center justify-between group block">
          <div>
            <div class="text-[10px] font-bold uppercase tracking-wider text-[#AA7000]">Benchmark Dossier</div>
            <div class="text-xs font-extrabold text-[#2C1F0E] group-hover:text-[#AA7000]">Google SDE-2 Report (89.5 / 100)</div>
            <div class="text-[10px] text-[#7F766C]">Calibrated Human Rubric &bull; Tri-Signal Biometrics</div>
          </div>
          <span class="material-symbols-outlined text-[#AA7000] text-lg group-hover:translate-x-0.5 transition-transform">arrow_forward</span>
        </a>

        <!-- Fast Mock User Switcher -->
        <div class="mt-3 pt-3 border-t border-[#E8DFD0]">
          <div class="text-[10px] font-bold uppercase tracking-wider text-[#7F766C] mb-2">Switch Candidate Persona</div>
          <div class="space-y-1.5">
            ${this.mockUsers.map(u => `
              <button type="button" onclick="window.userSession.setActiveUserById('${u.id}')" class="w-full p-2 rounded-xl border text-left flex items-center justify-between transition-all ${u.id === user.id ? 'bg-[#FAF6EE] border-[#AA7000] shadow-xs' : 'border-transparent hover:bg-[#FAF6EE] hover:border-[#E8DFD0]'}">
                <div class="flex items-center gap-2 min-w-0">
                  <div class="w-6 h-6 rounded-full overflow-hidden bg-[#2C1F0E] text-white text-[10px] font-bold flex items-center justify-center shrink-0">
                    <span>${u.initials}</span>
                  </div>
                  <div class="truncate">
                    <div class="text-xs font-bold text-[#2C1F0E] leading-tight">${u.name}</div>
                    <div class="text-[10px] text-[#7F766C]">${u.company} &bull; ${u.score} pts</div>
                  </div>
                </div>
                ${u.id === user.id ? '<span class="material-symbols-outlined text-xs text-[#AA7000]">check_circle</span>' : ''}
              </button>
            `).join('')}
          </div>
        </div>

        <!-- Navigation Actions -->
        <div class="mt-3 pt-3 border-t border-[#E8DFD0] grid grid-cols-2 gap-2 text-xs">
          <a href="settings.html" class="p-2 rounded-xl bg-[#FAF6EE] hover:bg-[#F2EBD8] text-[#2C1F0E] font-bold text-center flex items-center justify-center gap-1.5 transition-all">
            <span class="material-symbols-outlined text-base">settings</span>
            <span>Settings</span>
          </a>
          <button type="button" onclick="window.userSession.signOut()" class="p-2 rounded-xl bg-red-50 hover:bg-red-100 text-red-700 font-bold text-center flex items-center justify-center gap-1.5 transition-all">
            <span class="material-symbols-outlined text-base">logout</span>
            <span>Sign Out</span>
          </button>
        </div>
      </div>
    `;

    // Placement strategy:
    // 1. If an element with id `top-right-profile-slot` exists, put it there.
    // 2. Else if header exists, put it in header flex.
    // 3. Else inject fixed top-right badge.
    const slot = document.getElementById('top-right-profile-slot');
    if (slot) {
      slot.appendChild(widget);
    } else {
      const pageHeader = document.querySelector('header');
      if (pageHeader && !pageHeader.id.includes('interview-stage')) {
        const rightContainer = pageHeader.querySelector('.flex.items-center:last-child') || pageHeader;
        rightContainer.appendChild(widget);
      } else {
        // Floating fixed top-right position
        widget.classList.add('fixed', 'top-4', 'right-4');
        document.body.appendChild(widget);
      }
    }

    // Bind dropdown click behavior
    const trigger = document.getElementById('imaira-profile-trigger');
    const dropdown = document.getElementById('imaira-profile-dropdown');
    const caret = document.getElementById('imaira-badge-caret');

    if (trigger && dropdown) {
      trigger.addEventListener('click', (e) => {
        e.stopPropagation();
        const isHidden = dropdown.classList.contains('hidden');
        if (isHidden) {
          dropdown.classList.remove('hidden');
          if (caret) caret.textContent = 'expand_less';
        } else {
          dropdown.classList.add('hidden');
          if (caret) caret.textContent = 'expand_more';
        }
      });

      // Close dropdown when clicking outside
      document.addEventListener('click', (e) => {
        if (!widget.contains(e.target)) {
          dropdown.classList.add('hidden');
          if (caret) caret.textContent = 'expand_more';
        }
      });
    }

    this.syncUI();
  }

  syncUI() {
    const user = this.getActiveUser();

    // 1. Update top-right profile badge
    const badgeAvatar = document.getElementById('imaira-badge-avatar');
    const badgeInitials = document.getElementById('imaira-badge-initials');
    const badgeName = document.getElementById('imaira-badge-name');
    const badgeCompany = document.getElementById('imaira-badge-company');

    if (badgeAvatar) {
      if (user.avatar) {
        badgeAvatar.src = user.avatar;
        badgeAvatar.style.display = 'block';
        if (badgeInitials) badgeInitials.style.display = 'none';
      } else {
        badgeAvatar.style.display = 'none';
        if (badgeInitials) {
          badgeInitials.style.display = 'flex';
          badgeInitials.textContent = user.initials || 'RK';
        }
      }
    }
    if (badgeName) badgeName.textContent = user.name;
    if (badgeCompany) badgeCompany.textContent = (user.company || 'Google') + ' Target';

    // 2. Update modal details
    const modalName = document.getElementById('imaira-modal-name');
    const modalRole = document.getElementById('imaira-modal-role');
    const modalEmail = document.getElementById('imaira-modal-email');
    const modalAvatar = document.getElementById('imaira-modal-avatar');
    const modalInitials = document.getElementById('imaira-modal-initials');

    if (modalName) modalName.textContent = user.name;
    if (modalRole) modalRole.textContent = user.role;
    if (modalEmail) modalEmail.textContent = user.email;
    if (modalAvatar) {
      if (user.avatar) {
        modalAvatar.src = user.avatar;
        modalAvatar.style.display = 'block';
        if (modalInitials) modalInitials.style.display = 'none';
      } else {
        modalAvatar.style.display = 'none';
        if (modalInitials) {
          modalInitials.style.display = 'flex';
          modalInitials.textContent = user.initials || 'RK';
        }
      }
    }

    // 3. Update dashboard specific greeting & labels if present
    const dashGreeting = document.getElementById('dash-welcome-name');
    if (dashGreeting) dashGreeting.textContent = user.name;

    const dashTargetCompany = document.getElementById('dash-target-company');
    if (dashTargetCompany) dashTargetCompany.textContent = user.company || 'Google';

    const dashTargetRole = document.getElementById('dash-target-role');
    if (dashTargetRole) dashTargetRole.textContent = user.role;

    // 4. Update legacy sidebar if it exists on old view
    const sbName = document.getElementById('dash-sidebar-name');
    const sbRole = document.getElementById('dash-sidebar-role');
    const sbInitials = document.getElementById('dash-sidebar-initials');
    if (sbName) sbName.textContent = user.name;
    if (sbRole) sbRole.textContent = user.role;
    if (sbInitials) sbInitials.textContent = user.initials || 'RK';

    // 5. Update settings inputs if currently on settings page
    const setFullName = document.getElementById('set-full-name') || document.getElementById('profile-name');
    const setEmail = document.getElementById('set-email') || document.getElementById('profile-email');
    const setRole = document.getElementById('set-target-role') || document.getElementById('profile-role');
    const setCompany = document.getElementById('set-target-company') || document.getElementById('profile-company');
    const setBio = document.getElementById('set-bio') || document.getElementById('profile-bio');

    if (setFullName && !setFullName.dataset.userEdited) setFullName.value = user.name;
    if (setEmail && !setEmail.dataset.userEdited) setEmail.value = user.email;
    if (setRole && !setRole.dataset.userEdited) setRole.value = user.role;
    if (setCompany && !setCompany.dataset.userEdited) setCompany.value = user.company;
    if (setBio && !setBio.dataset.userEdited) setBio.value = user.bio || '';
  }

  signOut() {
    // Switch to Priya or clear session
    localStorage.removeItem(this.storageKey);
    window.location.href = 'auth.html';
  }
}

// Instantiate globally
window.userSession = new UserSessionManager();
