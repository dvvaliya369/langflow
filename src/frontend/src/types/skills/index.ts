export type ExternalSkill = {
  id: string;
  name: string;
  description: string;
  owner: string;
  repo: string;
  installs: number;
  category: string;
  url: string;
  installCommand: string;
};

export type ExternalSkillsResponse = {
  count: number;
  results: ExternalSkill[];
};

export type SkillsRegistryConfig = {
  registryUrl: string;
  enabled: boolean;
};
