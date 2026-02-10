import { create } from "zustand";
import { ENABLE_EXTERNAL_SKILLS } from "@/customization/feature-flags";
import type { ExternalSkill } from "@/types/skills";

const SKILLS_REGISTRY: ExternalSkill[] = [
  {
    id: "vercel-labs/skills/find-skills",
    name: "find-skills",
    description:
      "Search and discover skills from the open agent skills ecosystem. Find reusable skills for AI agents by keyword.",
    owner: "vercel-labs",
    repo: "skills",
    installs: 178900,
    category: "Discovery",
    url: "https://skills.sh/vercel-labs/skills/find-skills",
    installCommand: "npx skills add vercel-labs/skills",
  },
  {
    id: "vercel-labs/agent-skills/vercel-react-best-practices",
    name: "vercel-react-best-practices",
    description:
      "Best practices for building React applications with Vercel. Covers performance, patterns, and deployment strategies.",
    owner: "vercel-labs",
    repo: "agent-skills",
    installs: 116600,
    category: "Frontend",
    url: "https://skills.sh/vercel-labs/agent-skills/vercel-react-best-practices",
    installCommand: "npx skills add vercel-labs/agent-skills",
  },
  {
    id: "vercel-labs/agent-skills/web-design-guidelines",
    name: "web-design-guidelines",
    description:
      "Comprehensive web design guidelines for building modern, accessible, and responsive web applications.",
    owner: "vercel-labs",
    repo: "agent-skills",
    installs: 88100,
    category: "Design",
    url: "https://skills.sh/vercel-labs/agent-skills/web-design-guidelines",
    installCommand: "npx skills add vercel-labs/agent-skills",
  },
  {
    id: "remotion-dev/skills/remotion-best-practices",
    name: "remotion-best-practices",
    description:
      "Best practices for creating programmatic videos with Remotion. Covers composition, rendering, and optimization.",
    owner: "remotion-dev",
    repo: "skills",
    installs: 80800,
    category: "Media",
    url: "https://skills.sh/remotion-dev/skills/remotion-best-practices",
    installCommand: "npx skills add remotion-dev/skills",
  },
  {
    id: "anthropics/skills/frontend-design",
    name: "frontend-design",
    description:
      "Frontend design patterns and best practices for building beautiful, functional user interfaces.",
    owner: "anthropics",
    repo: "skills",
    installs: 57900,
    category: "Frontend",
    url: "https://skills.sh/anthropics/skills/frontend-design",
    installCommand: "npx skills add anthropics/skills",
  },
  {
    id: "vercel-labs/agent-skills/vercel-composition-patterns",
    name: "vercel-composition-patterns",
    description:
      "Advanced React composition patterns for building scalable and maintainable component architectures.",
    owner: "vercel-labs",
    repo: "agent-skills",
    installs: 33000,
    category: "Frontend",
    url: "https://skills.sh/vercel-labs/agent-skills/vercel-composition-patterns",
    installCommand: "npx skills add vercel-labs/agent-skills",
  },
  {
    id: "vercel-labs/agent-browser/agent-browser",
    name: "agent-browser",
    description:
      "Browser automation skill for AI agents. Navigate, interact with, and extract data from web pages.",
    owner: "vercel-labs",
    repo: "agent-browser",
    installs: 29100,
    category: "Automation",
    url: "https://skills.sh/vercel-labs/agent-browser/agent-browser",
    installCommand: "npx skills add vercel-labs/agent-browser",
  },
  {
    id: "anthropics/skills/skill-creator",
    name: "skill-creator",
    description:
      "Create and scaffold new custom skills for the open agent skills ecosystem.",
    owner: "anthropics",
    repo: "skills",
    installs: 28700,
    category: "Development",
    url: "https://skills.sh/anthropics/skills/skill-creator",
    installCommand: "npx skills add anthropics/skills",
  },
  {
    id: "browser-use/browser-use/browser-use",
    name: "browser-use",
    description:
      "Enable AI agents to use web browsers for research, data collection, and web-based task automation.",
    owner: "browser-use",
    repo: "browser-use",
    installs: 27700,
    category: "Automation",
    url: "https://skills.sh/browser-use/browser-use/browser-use",
    installCommand: "npx skills add browser-use/browser-use",
  },
  {
    id: "vercel-labs/agent-skills/vercel-react-native-skills",
    name: "vercel-react-native-skills",
    description:
      "Best practices and patterns for building React Native applications with Expo and Vercel.",
    owner: "vercel-labs",
    repo: "agent-skills",
    installs: 23800,
    category: "Mobile",
    url: "https://skills.sh/vercel-labs/agent-skills/vercel-react-native-skills",
    installCommand: "npx skills add vercel-labs/agent-skills",
  },
  {
    id: "expo/skills/expo-development",
    name: "expo-development",
    description:
      "Expo development best practices for building cross-platform mobile applications with React Native.",
    owner: "expo",
    repo: "skills",
    installs: 19500,
    category: "Mobile",
    url: "https://skills.sh/expo/skills/expo-development",
    installCommand: "npx skills add expo/skills",
  },
  {
    id: "antfu/skills/vue-best-practices",
    name: "vue-best-practices",
    description:
      "Vue.js and Vite ecosystem best practices, patterns, and development guidelines.",
    owner: "antfu",
    repo: "skills",
    installs: 15200,
    category: "Frontend",
    url: "https://skills.sh/antfu/skills/vue-best-practices",
    installCommand: "npx skills add antfu/skills",
  },
  {
    id: "google-labs-code/skills/testing-patterns",
    name: "testing-patterns",
    description:
      "Comprehensive testing patterns and strategies for unit, integration, and end-to-end testing.",
    owner: "google-labs-code",
    repo: "skills",
    installs: 12800,
    category: "Testing",
    url: "https://skills.sh/google-labs-code/skills/testing-patterns",
    installCommand: "npx skills add google-labs-code/skills",
  },
  {
    id: "better-auth/skills/auth-patterns",
    name: "auth-patterns",
    description:
      "Authentication and authorization patterns including OAuth, JWT, session management, and security best practices.",
    owner: "better-auth",
    repo: "skills",
    installs: 11400,
    category: "Security",
    url: "https://skills.sh/better-auth/skills/auth-patterns",
    installCommand: "npx skills add better-auth/skills",
  },
  {
    id: "black-forest-labs/skills/bfl-api",
    name: "bfl-api",
    description:
      "FLUX API integration for AI image generation and editing. Generate, edit, and transform images programmatically.",
    owner: "black-forest-labs",
    repo: "skills",
    installs: 9800,
    category: "AI/ML",
    url: "https://skills.sh/black-forest-labs/skills/bfl-api",
    installCommand: "npx skills add black-forest-labs/skills",
  },
];

const SKILL_CATEGORIES = [
  "All",
  "Frontend",
  "Design",
  "Automation",
  "Development",
  "Mobile",
  "Testing",
  "Security",
  "AI/ML",
  "Media",
  "Discovery",
];

export type SkillsStoreType = {
  hasSkills: boolean;
  skills: ExternalSkill[];
  filteredSkills: ExternalSkill[];
  categories: string[];
  loading: boolean;
  searchQuery: string;
  selectedCategory: string;
  sortOrder: string;
  registryUrl: string;
  setSearchQuery: (query: string) => void;
  setSelectedCategory: (category: string) => void;
  setSortOrder: (order: string) => void;
  setRegistryUrl: (url: string) => void;
  filterSkills: () => void;
  loadSkills: () => void;
};

export const useSkillsStore = create<SkillsStoreType>((set, get) => ({
  hasSkills: ENABLE_EXTERNAL_SKILLS,
  skills: [],
  filteredSkills: [],
  categories: SKILL_CATEGORIES,
  loading: false,
  searchQuery: "",
  selectedCategory: "All",
  sortOrder: "Popular",
  registryUrl: "https://skills.sh",

  setSearchQuery: (query: string) => {
    set({ searchQuery: query });
    get().filterSkills();
  },

  setSelectedCategory: (category: string) => {
    set({ selectedCategory: category });
    get().filterSkills();
  },

  setSortOrder: (order: string) => {
    set({ sortOrder: order });
    get().filterSkills();
  },

  setRegistryUrl: (url: string) => {
    set({ registryUrl: url });
  },

  filterSkills: () => {
    const { skills, searchQuery, selectedCategory, sortOrder } = get();
    let filtered = [...skills];

    if (selectedCategory !== "All") {
      filtered = filtered.filter(
        (skill) => skill.category === selectedCategory,
      );
    }

    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (skill) =>
          skill.name.toLowerCase().includes(query) ||
          skill.description.toLowerCase().includes(query) ||
          skill.owner.toLowerCase().includes(query) ||
          skill.category.toLowerCase().includes(query),
      );
    }

    if (sortOrder === "Popular") {
      filtered.sort((a, b) => b.installs - a.installs);
    } else if (sortOrder === "Alphabetical") {
      filtered.sort((a, b) => a.name.localeCompare(b.name));
    }

    set({ filteredSkills: filtered });
  },

  loadSkills: () => {
    set({ loading: true });
    // Load from built-in registry
    const skills = [...SKILLS_REGISTRY];
    set({ skills, loading: false });
    get().filterSkills();
  },
}));
