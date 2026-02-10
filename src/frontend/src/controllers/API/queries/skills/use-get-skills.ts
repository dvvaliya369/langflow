import type { useQueryFunctionType } from "@/types/api";
import type { ExternalSkill } from "@/types/skills";
import { useSkillsStore } from "@/stores/skillsStore";
import { UseRequestProcessor } from "../../services/request-processor";

type SkillsQueryResponse = ExternalSkill[];

export const useGetSkillsQuery: useQueryFunctionType<
  undefined,
  SkillsQueryResponse
> = (options) => {
  const { query } = UseRequestProcessor();
  const loadSkills = useSkillsStore((state) => state.loadSkills);

  const getSkillsFn = async (): Promise<SkillsQueryResponse> => {
    loadSkills();
    return useSkillsStore.getState().skills;
  };

  return query(["useGetSkillsQuery"], getSkillsFn, {
    refetchOnWindowFocus: false,
    ...options,
  });
};
