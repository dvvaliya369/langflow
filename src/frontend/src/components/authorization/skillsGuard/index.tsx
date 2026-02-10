import { CustomNavigate } from "@/customization/components/custom-navigate";
import { useSkillsStore } from "@/stores/skillsStore";

export const SkillsGuard = ({
  children,
}: {
  children: React.ReactNode;
}) => {
  const hasSkills = useSkillsStore((state) => state.hasSkills);

  if (!hasSkills) {
    return <CustomNavigate to="/all" replace />;
  }

  return children;
};
