import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CheckCircle2, Circle, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

const steps = [
  { id: 1, title: "Material Processing (RAG)", description: "Context retrieved from knowledge base", status: "pending" },
  { id: 2, title: "Script Generation (LLM)", description: "Writing narration & scene breakdown", status: "pending" },
  { id: 3, title: "Code Generation (Manim)", description: "Generating Python code for animations", status: "pending" },
  { id: 4, title: "Video Rendering (FFmpeg)", description: "Compiling final video output", status: "pending" },
];

export function Pipeline() {
  return (
    <Card className="w-full border shadow-sm bg-white">
      <CardHeader className="pb-3 border-b bg-gray-50/50">
        <CardTitle className="text-base font-semibold flex justify-between items-center">
            <span>Generation Pipeline</span>
            <span className="text-xs font-normal text-muted-foreground">Job ID: #8291A</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="grid gap-8 p-6">
        {steps.map((step, index) => (
          <div key={step.id} className="flex items-start gap-4 relative">
             {/* Line connector */}
            {index !== steps.length - 1 && (
                <div className="absolute left-[11px] top-7 h-full w-[2px] bg-gray-100" />
            )}
            
            <div className="relative z-10 flex h-6 w-6 items-center justify-center bg-white ring-4 ring-white">
                {step.status === "completed" && <CheckCircle2 className="h-6 w-6 text-green-500" />}
                {step.status === "processing" && <Loader2 className="h-6 w-6 text-indigo-600 animate-spin" />}
                {step.status === "pending" && <Circle className="h-6 w-6 text-gray-200" />}
            </div>
            <div className="grid gap-1 -mt-1">
              <p className={cn("text-sm font-medium leading-none", 
                  step.status === "pending" ? "text-gray-400" : "text-gray-900"
              )}>
                {step.title}
              </p>
              <p className="text-xs text-muted-foreground">
                {step.description}
              </p>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
