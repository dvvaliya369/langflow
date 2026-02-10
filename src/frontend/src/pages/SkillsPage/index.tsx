import { uniqueId } from "lodash";
import { useEffect, useState } from "react";
import SkillCardComponent from "@/components/common/skillCardComponent";
import IconComponent from "@/components/common/genericIconComponent";
import PageLayout from "@/components/common/pageLayout";
import { SkeletonCardComponent } from "@/components/common/skeletonCardComponent";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useSkillsStore } from "@/stores/skillsStore";
import InputSearchComponent from "../MainPage/components/inputSearchComponent";

export default function SkillsPage(): JSX.Element {
  const skills = useSkillsStore((state) => state.filteredSkills);
  const categories = useSkillsStore((state) => state.categories);
  const loading = useSkillsStore((state) => state.loading);
  const searchQuery = useSkillsStore((state) => state.searchQuery);
  const selectedCategory = useSkillsStore((state) => state.selectedCategory);
  const sortOrder = useSkillsStore((state) => state.sortOrder);
  const loadSkills = useSkillsStore((state) => state.loadSkills);
  const setSearchQuery = useSkillsStore((state) => state.setSearchQuery);
  const setSelectedCategory = useSkillsStore(
    (state) => state.setSelectedCategory,
  );
  const setSortOrder = useSkillsStore((state) => state.setSortOrder);
  const registryUrl = useSkillsStore((state) => state.registryUrl);

  const [inputText, setInputText] = useState<string>("");

  useEffect(() => {
    loadSkills();
  }, []);

  const handleSearch = () => {
    setSearchQuery(inputText);
  };

  return (
    <PageLayout
      betaIcon
      title="External Skills"
      description="Discover and integrate external skills from the open agent skills ecosystem."
      button={
        <Button
          data-testid="skills-registry-button"
          variant="primary"
          onClick={() => {
            window.open(registryUrl, "_blank", "noopener,noreferrer");
          }}
        >
          <IconComponent name="ExternalLink" className="mr-2 w-4" />
          Browse Registry
        </Button>
      }
    >
      <div className="flex h-full w-full flex-col justify-between">
        <div className="flex w-full flex-col gap-4 p-0">
          <div className="flex items-end gap-4">
            <InputSearchComponent
              loading={loading}
              divClasses="relative h-12 w-[40%]"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  handleSearch();
                }
              }}
              onClick={handleSearch}
            />
            <div className="ml-4 flex w-full gap-2 border-b border-border">
              {categories.map((category) => (
                <button
                  key={category}
                  data-testid={`category-${category.toLowerCase()}-button`}
                  disabled={loading}
                  onClick={() => {
                    setSelectedCategory(category);
                  }}
                  className={
                    (selectedCategory === category
                      ? "border-b-2 border-primary p-3"
                      : "border-b-2 border-transparent p-3 text-muted-foreground hover:text-primary") +
                    (loading ? " cursor-not-allowed" : "")
                  }
                >
                  {category}
                </button>
              ))}
            </div>
          </div>

          <div className="flex items-end justify-between">
            <span className="px-0.5 text-sm text-muted-foreground">
              {!loading && (
                <>
                  {skills.length} {skills.length !== 1 ? "skills" : "skill"}{" "}
                  found
                </>
              )}
            </span>

            <Select
              disabled={loading}
              onValueChange={(e) => {
                setSortOrder(e);
              }}
              value={sortOrder}
            >
              <SelectTrigger data-testid="select-order-skills">
                <SelectValue placeholder="Popular" />
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  <SelectItem value="Popular">Popular</SelectItem>
                  <SelectItem value="Alphabetical">Alphabetical</SelectItem>
                </SelectGroup>
              </SelectContent>
            </Select>
          </div>

          <div className="grid w-full gap-4 md:grid-cols-2 lg:grid-cols-3">
            {!loading ? (
              skills.map((item) => (
                <SkillCardComponent
                  key={item.id}
                  data={item}
                  disabled={loading}
                />
              ))
            ) : (
              <>
                <SkeletonCardComponent />
                <SkeletonCardComponent />
                <SkeletonCardComponent />
              </>
            )}
          </div>

          {!loading && skills.length === 0 && (
            <div className="mt-6 flex w-full items-center justify-center text-center">
              <div className="flex h-full w-full flex-col">
                <div className="flex w-full flex-col gap-4">
                  <div className="grid w-full gap-4">
                    No skills found matching your search criteria. Try a
                    different search term or category.
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </PageLayout>
  );
}
