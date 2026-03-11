


import { Lead, SniperTarget, ContentPiece, UserProfile, Candidate, ContractAudit, Invoice, ViralStrategyResult } from '../types';

// --- INITIAL SEED DATA ---

const INITIAL_ADMIN: UserProfile = {
  id: 'admin-1',
  name: 'Majen Olivera',
  email: 'majen@yokaizen.ai',
  password: '', // Password should be handled securely by the backend
  role: 'ADMIN',
  status: 'ACTIVE',
  lastLogin: new Date().toISOString(),
  plan: 'ENTERPRISE',
  apiMode: 'PLATFORM',
  credits: 5000 // Admin gets lots of credits
};

const INITIAL_TARGETS: SniperTarget[] = [
  {
    id: '1',
    name: 'Alice Freeman',
    linkedinUrl: 'linkedin.com/in/alicefreeman',
    rawProfileText: 'VP of Engineering at CloudScale. Recently posted about the difficulties of migrating legacy SQL databases to NoSQL. Passionate about mountain biking.',
    icebreaker: null,
    status: 'NEW'
  }
];

const INITIAL_LEADS: Lead[] = [
  {
    id: '101',
    name: 'John Doe',
    email: 'john@enterprise.com',
    message: 'Hi, we are a team of 50 looking to migrate our entire CRM. Budget is allocated for Q3.',
    status: 'PENDING',
    timestamp: new Date()
  }
];

// --- STORAGE KEYS ---
const KEYS = {
  USERS_DB: 'yokaizen_users_db', // All users
  SESSION: 'yokaizen_session',   // Current logged in user
  TARGETS: 'yokaizen_targets',
  LEADS: 'yokaizen_leads',
  CONTENT: 'yokaizen_content',
  CANDIDATES: 'yokaizen_candidates',
  CONTRACTS: 'yokaizen_contracts',
  INVOICES: 'yokaizen_invoices',
  VIRAL_STRATEGIES: 'yokaizen_viral_strategies'
};

// --- TYPES FOR AUTH ---
export interface AuthResponse {
  success: boolean;
  message?: string;
  user?: UserProfile;
}

export const StorageService = {
  // --- AUTHENTICATION & USER MANAGEMENT ---

  // Initialize DB with Admin if empty
  init: () => {
    const users = localStorage.getItem(KEYS.USERS_DB);
    if (!users) {
      localStorage.setItem(KEYS.USERS_DB, JSON.stringify([INITIAL_ADMIN]));
    }
  },

  getAllUsers: (): UserProfile[] => {
    StorageService.init();
    const stored = localStorage.getItem(KEYS.USERS_DB);
    return stored ? JSON.parse(stored) : [INITIAL_ADMIN];
  },

  getUser: (): UserProfile | null => {
    const stored = localStorage.getItem(KEYS.SESSION);
    return stored ? JSON.parse(stored) : null; // Return null if no session
  },

  login: (email: string, password: string): AuthResponse => {
    const users = StorageService.getAllUsers();
    const user = users.find(u => u.email.toLowerCase() === email.toLowerCase());

    if (user && user.password === password) {
      if (user.status === 'SUSPENDED') {
        return { success: false, message: 'Account suspended. Contact support.' };
      }

      // Update last login
      user.lastLogin = new Date().toISOString();

      // Ensure new fields exist for legacy users
      if (!user.apiMode) {
        user.apiMode = 'PLATFORM';
        user.credits = 100;
      }

      StorageService.updateUserInDb(user);

      // Set Session
      localStorage.setItem(KEYS.SESSION, JSON.stringify(user));
      window.dispatchEvent(new Event('user-update'));
      return { success: true, user };
    }

    return { success: false, message: 'Invalid credentials' };
  },

  register: (name: string, email: string, password: string): AuthResponse => {
    const users = StorageService.getAllUsers();
    if (users.find(u => u.email.toLowerCase() === email.toLowerCase())) {
      return { success: false, message: 'Email already exists' };
    }

    const newUser: UserProfile = {
      id: Date.now().toString(),
      name,
      email,
      password,
      role: 'USER', // Default role
      status: 'ACTIVE',
      lastLogin: new Date().toISOString(),
      plan: 'STARTER', // Default to paid starter plan
      apiMode: 'PLATFORM',
      credits: 0 // No free credits, must top up
    };

    users.push(newUser);
    localStorage.setItem(KEYS.USERS_DB, JSON.stringify(users));

    // Auto-login
    localStorage.setItem(KEYS.SESSION, JSON.stringify(newUser));
    window.dispatchEvent(new Event('user-update'));

    return { success: true, user: newUser };
  },

  logout: () => {
    localStorage.removeItem(KEYS.SESSION);
    window.dispatchEvent(new Event('user-update'));
  },

  // Simulate Password Recovery
  recoverPassword: (email: string): AuthResponse => {
    const users = StorageService.getAllUsers();
    const user = users.find(u => u.email.toLowerCase() === email.toLowerCase());

    if (user) {
      // In a real app, call backend API to send email
      console.log(`Sending password reset email to ${email}`);
      return { success: true, message: 'Recovery email sent' };
    }
    return { success: false, message: 'Email not found' };
  },

  resetPassword: (email: string, newPassword: string): AuthResponse => {
    const users = StorageService.getAllUsers();
    const userIndex = users.findIndex(u => u.email.toLowerCase() === email.toLowerCase());

    if (userIndex > -1) {
      users[userIndex].password = newPassword;
      localStorage.setItem(KEYS.USERS_DB, JSON.stringify(users));
      return { success: true, message: 'Password updated successfully' };
    }
    return { success: false, message: 'User not found' };
  },

  // --- ADMIN FUNCTIONS ---

  updateUserInDb: (updatedUser: UserProfile) => {
    const users = StorageService.getAllUsers();
    const index = users.findIndex(u => u.id === updatedUser.id);
    if (index > -1) {
      users[index] = updatedUser;
      localStorage.setItem(KEYS.USERS_DB, JSON.stringify(users));

      // If updating current session user, update session too
      const current = StorageService.getUser();
      if (current && current.id === updatedUser.id) {
        localStorage.setItem(KEYS.SESSION, JSON.stringify(updatedUser));
        window.dispatchEvent(new Event('user-update'));
      }
    }
  },

  deleteUser: (userId: string) => {
    const users = StorageService.getAllUsers();
    const newUsers = users.filter(u => u.id !== userId);
    localStorage.setItem(KEYS.USERS_DB, JSON.stringify(newUsers));
  },

  deductCredits: (amount: number) => {
    const user = StorageService.getUser();
    if (!user) return;
    if (user.apiMode === 'PLATFORM') {
      user.credits = Math.max(0, (user.credits || 0) - amount);
      StorageService.updateUserInDb(user);
    }
  },

  // --- AGENT DATA ---

  // Sniper Targets
  getTargets: (): SniperTarget[] => {
    const stored = localStorage.getItem(KEYS.TARGETS);
    return stored ? JSON.parse(stored) : INITIAL_TARGETS;
  },
  saveTargets: (targets: SniperTarget[]) => {
    localStorage.setItem(KEYS.TARGETS, JSON.stringify(targets));
  },
  addTarget: (target: SniperTarget) => {
    const current = StorageService.getTargets();
    StorageService.saveTargets([target, ...current]);
  },
  updateTarget: (updated: SniperTarget) => {
    const current = StorageService.getTargets();
    const newTargets = current.map(t => t.id === updated.id ? updated : t);
    StorageService.saveTargets(newTargets);
  },
  deleteTarget: (id: string) => {
    const current = StorageService.getTargets();
    StorageService.saveTargets(current.filter(t => t.id !== id));
  },

  // Gatekeeper Leads
  getLeads: (): Lead[] => {
    const stored = localStorage.getItem(KEYS.LEADS);
    if (!stored) return INITIAL_LEADS;
    return JSON.parse(stored).map((l: any) => ({ ...l, timestamp: new Date(l.timestamp) }));
  },
  saveLeads: (leads: Lead[]) => {
    localStorage.setItem(KEYS.LEADS, JSON.stringify(leads));
  },
  addLead: (lead: Lead) => {
    const current = StorageService.getLeads();
    StorageService.saveLeads([lead, ...current]);
  },
  updateLead: (updated: Lead) => {
    const current = StorageService.getLeads();
    StorageService.saveLeads(current.map(l => l.id === updated.id ? updated : l));
  },

  // Content History
  getContent: (): ContentPiece[] => {
    const stored = localStorage.getItem(KEYS.CONTENT);
    if (!stored) return [];
    return JSON.parse(stored).map((c: any) => ({ ...c, createdAt: new Date(c.createdAt) }));
  },
  saveContent: (piece: ContentPiece) => {
    const current = StorageService.getContent();
    localStorage.setItem(KEYS.CONTENT, JSON.stringify([piece, ...current]));
  },

  // -- NEW AGENTS STORAGE --

  // Recruiting
  getCandidates: (): Candidate[] => {
    const stored = localStorage.getItem(KEYS.CANDIDATES);
    return stored ? JSON.parse(stored) : [];
  },
  saveCandidate: (c: Candidate) => {
    const current = StorageService.getCandidates();
    localStorage.setItem(KEYS.CANDIDATES, JSON.stringify([c, ...current.filter(i => i.id !== c.id)]));
  },

  // Legal
  getContracts: (): ContractAudit[] => {
    const stored = localStorage.getItem(KEYS.CONTRACTS);
    return stored ? JSON.parse(stored) : [];
  },
  saveContract: (c: ContractAudit) => {
    const current = StorageService.getContracts();
    localStorage.setItem(KEYS.CONTRACTS, JSON.stringify([c, ...current.filter(i => i.id !== c.id)]));
  },

  // Procurement
  getInvoices: (): Invoice[] => {
    const stored = localStorage.getItem(KEYS.INVOICES);
    return stored ? JSON.parse(stored) : [];
  },
  saveInvoice: (inv: Invoice) => {
    const current = StorageService.getInvoices();
    localStorage.setItem(KEYS.INVOICES, JSON.stringify([inv, ...current.filter(i => i.id !== inv.id)]));
  },

  // Viral Growth Strategies
  getViralStrategies: (): { id: string, url: string, date: string, strategy: ViralStrategyResult }[] => {
    const stored = localStorage.getItem(KEYS.VIRAL_STRATEGIES);
    return stored ? JSON.parse(stored) : [];
  },
  saveViralStrategy: (strategy: ViralStrategyResult, url: string) => {
    const current = StorageService.getViralStrategies();
    const newItem = {
      id: Date.now().toString(),
      url,
      date: new Date().toISOString(),
      strategy
    };
    localStorage.setItem(KEYS.VIRAL_STRATEGIES, JSON.stringify([newItem, ...current]));
  },

  // Dashboard Stats
  getDashboardStats: () => {
    const leads = StorageService.getLeads();
    const content = StorageService.getContent();
    const users = StorageService.getAllUsers();

    return {
      totalLeads: leads.length,
      qualifiedLeads: leads.filter(l => l.status === 'QUALIFIED').length,
      contentGenerated: content.length,
      savedMoney: (leads.length * 5) + (content.length * 50),
      totalUsers: users.length
    };
  },

  // Onboarding
  isOnboardingComplete: (): boolean => {
    const user = StorageService.getUser();
    if (!user) return true; // No user = no onboarding
    return localStorage.getItem(`yokaizen_onboarding_${user.id}`) === 'true';
  },

  setOnboardingComplete: (complete: boolean) => {
    const user = StorageService.getUser();
    if (!user) return;
    localStorage.setItem(`yokaizen_onboarding_${user.id}`, complete.toString());
  }
};
