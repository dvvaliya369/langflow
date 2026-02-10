import { useState } from "react";
import useAlertStore from "@/stores/alertStore";
import type { ExternalSkill } from "@/types/skills";
import { cn } from "@/utils/utils";
import { Button } from "../../ui/button";
import {
  Card,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "../../ui/card";
import IconComponent from "../genericIconComponent";
import ShadTooltip from "../shadTooltipComponent";

function formatInstalls(count: number): string {
  if (count >= 1000000) {
    return `${(count / 1000000).toFixed(1)}M`;
  }
  if (count >= 1000) {
    return `${(count / 1000).toFixed(1)}K`;
  }
  return count.toString();
}

function getCategoryColor(category: string): string {
  const colors: Record<string, string> = {
    Frontend: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
    Design:
      "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
    Automation:
      "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
    Development:
      "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
    Mobile:
      "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
    Testing: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
    Security:
      "bg-slate-100 text-slate-800 dark:bg-slate-900 dark:text-slate-200",
    "AI/ML":
      "bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200",
    Media: "bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200",
    Discovery:
      "bg-teal-100 text-teal-800 dark:bg-teal-900 dark:text-teal-200",
  };
  return (
    colors[category] ??
    "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200"
  );
}

export default function SkillCardComponent({
  data,
  disabled = false,
}: {
  data: ExternalSkill;
  disabled?: boolean;
}) {
  const setSuccessData = useAlertStore((state) => state.setSuccessData);
  const [copied, setCopied] = useState(false);

  const handleCopyCommand = async () => {
    try {
      await navigator.clipboard.writeText(data.installCommand);
      setCopied(true);
      setSuccessData({
        title: `Install command copied to clipboard`,
      });
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback for environments without clipboard API
      setSuccessData({
        title: `Install with: ${data.installCommand}`,
      });
    }
  };

  const handleOpenSkillPage = () => {
    window.open(data.url, "_blank", "noopener,noreferrer");
  };

  return (
    <Card
      data-testid={`skill-card-${data.name}`}
      className={cn(
        "group relative flex h-[14rem] flex-col justify-between overflow-hidden transition-all hover:bg-muted/50 hover:shadow-md hover:dark:bg-[#5f5f5f0e]",
        disabled ? "pointer-events-none opacity-50" : "",
      )}
    >
      <div>
        <CardHeader>
          <div>
            <CardTitle className="flex w-full items-start justify-between gap-3 text-xl">
              <IconComponent
                className="visible mx-0.5 h-6 w-6 flex-shrink-0 text-primary"
                name="Zap"
              />
              <ShadTooltip content={data.name}>
                <div className="w-full truncate pr-3">{data.name}</div>
              </ShadTooltip>
              <div className="flex items-center gap-3">
                <ShadTooltip content="Installs">
                  <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
                    <IconComponent name="DownloadCloud" className="h-4 w-4" />
                    <span data-testid={`installs-${data.name}`}>
                      {formatInstalls(data.installs)}
                    </span>
                  </span>
                </ShadTooltip>
              </div>
            </CardTitle>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-primary">
              by <b>{data.owner}</b>
            </span>
            <span
              className={cn(
                "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium",
                getCategoryColor(data.category),
              )}
            >
              {data.category}
            </span>
          </div>
          <CardDescription className="pb-2 pt-2">
            <div className="truncate-doubleline">{data.description}</div>
          </CardDescription>
        </CardHeader>
      </div>

      <CardFooter>
        <div className="z-50 flex w-full items-center justify-between gap-2">
          <code className="truncate rounded bg-muted px-2 py-1 text-xs text-muted-foreground">
            {data.installCommand}
          </code>
          <div className="flex flex-wrap items-end justify-end gap-0.5">
            <ShadTooltip content="View on skills.sh">
              <Button
                variant="ghost"
                size="icon"
                className="whitespace-nowrap"
                onClick={handleOpenSkillPage}
                data-testid={`view-${data.name}`}
              >
                <IconComponent name="ExternalLink" className="h-5 w-5" />
              </Button>
            </ShadTooltip>
            <ShadTooltip
              content={copied ? "Copied!" : "Copy install command"}
            >
              <Button
                variant="ghost"
                size="icon"
                className="whitespace-nowrap"
                onClick={handleCopyCommand}
                data-testid={`install-${data.name}`}
              >
                <IconComponent
                  name={copied ? "Check" : "Copy"}
                  className="h-5 w-5"
                />
              </Button>
            </ShadTooltip>
          </div>
        </div>
      </CardFooter>
    </Card>
  );
}
