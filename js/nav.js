/**
 * Navigation Authentication Handler
 * COT Pulse - Shared across all pages
 */

const NAV_API_URL = 'https://cot-pulse-backend-production.up.railway.app';

/**
 * Check if user is logged in
 */
function isUserLoggedIn() {
    return !!localStorage.getItem('token');
}

/**
 * Get stored user data
 */
function getStoredUser() {
    try {
        return JSON.parse(localStorage.getItem('user') || '{}');
    } catch {
        return {};
    }
}

/**
 * Get auth token
 */
function getAuthToken() {
    return localStorage.getItem('token');
}

/**
 * Logout user
 */
function logoutUser() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/';
}

/**
 * Fetch fresh user data from API
 */
async function fetchUserData() {
    const token = getAuthToken();
    if (!token) return null;

    try {
        const response = await fetch(`${NAV_API_URL}/api/auth/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            if (response.status === 401 || response.status === 403) {
                // Token expired, clear and redirect
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                return null;
            }
            throw new Error('Failed to fetch user data');
        }

        const data = await response.json();
        if (data.success && data.user) {
            // Update stored user data
            localStorage.setItem('user', JSON.stringify(data.user));
            return data.user;
        }
        return null;
    } catch (error) {
        console.error('[Nav] Error fetching user data:', error);
        return null;
    }
}

/**
 * Create profile dropdown HTML
 */
function createProfileDropdown(user) {
    const name = user.name || user.email?.split('@')[0] || 'User';
    const tier = user.subscriptionTier || 'free';
    const tierLabel = tier === 'pro' ? 'Pro' : 'Free';
    const tierClass = tier === 'pro' ? 'tier-pro' : 'tier-free';

    return `
        <div class="profile-dropdown" id="profile-dropdown">
            <button class="profile-btn" id="profile-btn" onclick="toggleProfileMenu()">
                <div class="profile-avatar">${name.charAt(0).toUpperCase()}</div>
                <span class="profile-name">${name}</span>
                <svg class="dropdown-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M6 9l6 6 6-6"/>
                </svg>
            </button>
            <div class="profile-menu" id="profile-menu">
                <div class="profile-header">
                    <div class="profile-avatar-lg">${name.charAt(0).toUpperCase()}</div>
                    <div class="profile-info">
                        <div class="profile-name-lg">${name}</div>
                        <div class="profile-email">${user.email || ''}</div>
                        <span class="subscription-badge ${tierClass}">${tierLabel}</span>
                    </div>
                </div>
                <div class="profile-menu-items">
                    <a href="/settings" class="profile-menu-item">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="12" cy="12" r="3"/>
                            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
                        </svg>
                        Settings
                    </a>
                    <a href="/pricing" class="profile-menu-item">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
                        </svg>
                        ${tier === 'pro' ? 'Manage Plan' : 'Upgrade to Pro'}
                    </a>
                    <button onclick="logoutUser()" class="profile-menu-item logout-btn">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
                            <polyline points="16 17 21 12 16 7"/>
                            <line x1="21" y1="12" x2="9" y2="12"/>
                        </svg>
                        Logout
                    </button>
                </div>
            </div>
        </div>
    `;
}

/**
 * Toggle profile menu visibility
 */
function toggleProfileMenu() {
    const menu = document.getElementById('profile-menu');
    if (menu) {
        menu.classList.toggle('show');
    }
}

/**
 * Close profile menu when clicking outside
 */
document.addEventListener('click', (e) => {
    const dropdown = document.getElementById('profile-dropdown');
    const menu = document.getElementById('profile-menu');

    if (dropdown && menu && !dropdown.contains(e.target)) {
        menu.classList.remove('show');
    }
});

/**
 * Update navigation based on auth state
 */
async function updateNavigation() {
    const authButtons = document.querySelector('.auth-buttons');
    const headerActions = document.querySelector('.header-actions');

    if (!authButtons && !headerActions) {
        console.log('[Nav] No navigation container found');
        return;
    }

    const container = authButtons || headerActions;

    if (isUserLoggedIn()) {
        // User is logged in
        let user = getStoredUser();

        // If no stored user data, fetch it
        if (!user.email) {
            user = await fetchUserData();
            if (!user) {
                // Token invalid, show login buttons
                return;
            }
        }

        // Replace auth buttons with profile dropdown
        container.innerHTML = createProfileDropdown(user);

    } else {
        // User is logged out - ensure login/signup buttons are visible
        if (!container.querySelector('a[href="/login"]')) {
            container.innerHTML = `
                <a href="/login" class="btn btn-ghost">Login</a>
                <a href="/signup" class="btn btn-primary">Sign Up</a>
            `;
        }
    }
}

/**
 * Add profile dropdown styles to page
 */
function addProfileStyles() {
    if (document.getElementById('profile-dropdown-styles')) return;

    const styles = document.createElement('style');
    styles.id = 'profile-dropdown-styles';
    styles.textContent = `
        .profile-dropdown {
            position: relative;
        }

        .profile-btn {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 6px 12px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            color: var(--text-primary, #E6E9F0);
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
        }

        .profile-btn:hover {
            background: rgba(255, 255, 255, 0.1);
            border-color: rgba(255, 255, 255, 0.2);
        }

        .profile-avatar {
            width: 28px;
            height: 28px;
            background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: 600;
            color: white;
        }

        .profile-name {
            max-width: 120px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .dropdown-arrow {
            transition: transform 0.2s;
        }

        .profile-menu.show + .profile-btn .dropdown-arrow,
        .profile-btn:focus .dropdown-arrow {
            transform: rotate(180deg);
        }

        .profile-menu {
            position: absolute;
            top: calc(100% + 8px);
            right: 0;
            width: 280px;
            background: #1a1f2e;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
            opacity: 0;
            visibility: hidden;
            transform: translateY(-10px);
            transition: all 0.2s;
            z-index: 1000;
        }

        .profile-menu.show {
            opacity: 1;
            visibility: visible;
            transform: translateY(0);
        }

        .profile-header {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 16px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        }

        .profile-avatar-lg {
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            font-weight: 600;
            color: white;
            flex-shrink: 0;
        }

        .profile-info {
            overflow: hidden;
        }

        .profile-name-lg {
            font-size: 14px;
            font-weight: 600;
            color: var(--text-primary, #E6E9F0);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .profile-email {
            font-size: 12px;
            color: var(--text-secondary, #9AA3B2);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            margin-bottom: 6px;
        }

        .subscription-badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .subscription-badge.tier-free {
            background: rgba(107, 114, 128, 0.2);
            color: #9ca3af;
        }

        .subscription-badge.tier-pro {
            background: rgba(59, 130, 246, 0.2);
            color: #60a5fa;
        }

        .profile-menu-items {
            padding: 8px;
        }

        .profile-menu-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 12px;
            border-radius: 8px;
            color: var(--text-secondary, #9AA3B2);
            text-decoration: none;
            font-size: 14px;
            transition: all 0.15s;
            width: 100%;
            border: none;
            background: none;
            cursor: pointer;
            text-align: left;
        }

        .profile-menu-item:hover {
            background: rgba(255, 255, 255, 0.05);
            color: var(--text-primary, #E6E9F0);
        }

        .profile-menu-item.logout-btn {
            color: #f87171;
        }

        .profile-menu-item.logout-btn:hover {
            background: rgba(248, 113, 113, 0.1);
            color: #fca5a5;
        }

        /* For pricing.html header-actions */
        .header-actions .profile-dropdown {
            display: flex;
        }

        .header-actions .btn-login,
        .header-actions .btn-signup {
            /* Keep existing styles */
        }
    `;
    document.head.appendChild(styles);
}

// Initialize navigation on page load
document.addEventListener('DOMContentLoaded', () => {
    addProfileStyles();
    updateNavigation();
});
