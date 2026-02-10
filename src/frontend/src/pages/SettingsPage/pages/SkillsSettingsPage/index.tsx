import { useState } from "react";
import ForwardedIconComponent from "@/components/common/genericIconComponent";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import useAlertStore from "@/stores/alertStore";
import { useSkillsStore } from "@/stores/skillsStore";

export default function SkillsSettingsPage(): JSX.Element {
  const registryUrl = useSkillsStore((state) => state.registryUrl);
  const setRegistryUrl = useSkillsStore((state) => state.setRegistryUrl);
  const setSuccessData = useAlertStore((state) => state.setSuccessData);

  const [urlInput, setUrlInput] = useState(registryUrl);

  const handleSave = () => {
    setRegistryUrl(urlInput);
    setSuccessData({
      title: "Skills registry URL updated successfully.",
    });
  };

  return (
    <div className="flex h-full w-full flex-col gap-6">
      <div className="flex flex-col gap-2">
        <h3 className="text-lg font-semibold tracking-tight">
          External Skills
        </h3>
        <p className="text-sm text-muted-foreground">
          Configure the external skills registry integration. Skills extend
          Langflow with reusable agent capabilities from the open ecosystem at{" "}
          <a
            href="https://skills.sh"
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary underline"
          >
            skills.sh
          </a>
          .
        </p>
      </div>

      <div className="flex flex-col gap-4">
        <div className="flex flex-col gap-2">
          <label
            htmlFor="registry-url"
            className="text-sm font-medium leading-none"
          >
            Skills Registry URL
          </label>
          <div className="flex gap-2">
            <Input
              id="registry-url"
              data-testid="skills-registry-url-input"
              placeholder="https://skills.sh"
              value={urlInput}
              onChange={(e) => setUrlInput(e.target.value)}
              className="max-w-md"
            />
            <Button
              data-testid="save-skills-registry-url"
              variant="primary"
              onClick={handleSave}
            >
              Save
            </Button>
          </div>
          <p className="text-xs text-muted-foreground">
            The base URL for the skills registry. Default is
            https://skills.sh.
          </p>
        </div>

        <div className="flex flex-col gap-2 rounded-lg border p-4">
          <h4 className="text-sm font-medium">Quick Start</h4>
          <p className="text-sm text-muted-foreground">
            Install skills using the CLI. Run the following command in your
            terminal:
          </p>
          <div className="flex items-center gap-2">
            <code className="flex-1 rounded bg-muted px-3 py-2 text-sm">
              npx skills add &lt;owner/repo&gt;
            </code>
          </div>
          <p className="text-sm text-muted-foreground">
            Search for available skills:
          </p>
          <div className="flex items-center gap-2">
            <code className="flex-1 rounded bg-muted px-3 py-2 text-sm">
              npx skills find [query]
            </code>
          </div>
        </div>

        <div className="flex flex-col gap-2 rounded-lg border p-4">
          <h4 className="text-sm font-medium">Available Commands</h4>
          <div className="grid gap-2 text-sm">
            <div className="flex items-start gap-3">
              <code className="min-w-[180px] rounded bg-muted px-2 py-1 text-xs">
                npx skills find [query]
              </code>
              <span className="text-muted-foreground">
                Search for skills by keyword
              </span>
            </div>
            <div className="flex items-start gap-3">
              <code className="min-w-[180px] rounded bg-muted px-2 py-1 text-xs">
                npx skills add &lt;package&gt;
              </code>
              <span className="text-muted-foreground">
                Install a skill from the registry
              </span>
            </div>
            <div className="flex items-start gap-3">
              <code className="min-w-[180px] rounded bg-muted px-2 py-1 text-xs">
                npx skills check
              </code>
              <span className="text-muted-foreground">
                Check for skill updates
              </span>
            </div>
            <div className="flex items-start gap-3">
              <code className="min-w-[180px] rounded bg-muted px-2 py-1 text-xs">
                npx skills update
              </code>
              <span className="text-muted-foreground">
                Update all installed skills
              </span>
            </div>
            <div className="flex items-start gap-3">
              <code className="min-w-[180px] rounded bg-muted px-2 py-1 text-xs">
                npx skills init
              </code>
              <span className="text-muted-foreground">
                Scaffold a new custom skill
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
