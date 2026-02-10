import type { useMutationFunctionType } from "@/types/api";
import { UseRequestProcessor } from "../../services/request-processor";

interface IInstallSkill {
  skillId: string;
  installCommand: string;
}

interface IInstallSkillResponse {
  success: boolean;
  command: string;
}

export const useInstallSkill: useMutationFunctionType<
  undefined,
  IInstallSkill,
  IInstallSkillResponse
> = (options) => {
  const { mutate } = UseRequestProcessor();

  const installSkillFn = async (
    payload: IInstallSkill,
  ): Promise<IInstallSkillResponse> => {
    // Return the install command for the user to execute
    return {
      success: true,
      command: payload.installCommand,
    };
  };

  return mutate(["useInstallSkill"], installSkillFn, options);
};
